from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

import httpx
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qdrant_models

from app.core.config import Settings
from app.core.exceptions import BadRequestError
from app.core.exceptions import ConfigurationError
from app.core.exceptions import NotFoundError
from app.core.exceptions import ServiceUnavailableError
from app.schemas.rag_schema import RagHealthResponse
from app.schemas.rag_schema import RagIndexResponse
from app.schemas.rag_schema import RagQueryRequest
from app.schemas.rag_schema import RagQueryResponse
from app.schemas.rag_schema import RagSourceChunk


SUPPORTED_DOCUMENT_SUFFIXES = {".md", ".txt"}


@dataclass(slots=True)
class SourceDocument:
    doc_id: str
    source: str
    title: str
    text: str


@dataclass(slots=True)
class DocumentChunk:
    doc_id: str
    source: str
    title: str
    chunk_index: int
    text: str


class RagService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = self.settings.OLLAMA_BASE_URL.rstrip("/")
        self.timeout = httpx.Timeout(self.settings.OLLAMA_TIMEOUT_SECONDS)
        self.qdrant_client = AsyncQdrantClient(url=self.settings.QDRANT_URL, timeout=30.0)

    async def get_health(self) -> RagHealthResponse:
        ollama_healthy = await self._check_ollama_health()
        qdrant_healthy = await self._check_qdrant_health()
        collection_exists = False
        indexed_points = 0

        if qdrant_healthy:
            try:
                collection_exists = await self.qdrant_client.collection_exists(
                    collection_name=self.settings.QDRANT_COLLECTION_NAME
                )
                if collection_exists:
                    count_result = await self.qdrant_client.count(
                        collection_name=self.settings.QDRANT_COLLECTION_NAME,
                        exact=True,
                    )
                    indexed_points = count_result.count
            except Exception:
                qdrant_healthy = False

        status = "healthy" if ollama_healthy and qdrant_healthy else "degraded"

        return RagHealthResponse(
            status=status,
            ollama="connected" if ollama_healthy else "disconnected",
            qdrant="connected" if qdrant_healthy else "disconnected",
            collection_name=self.settings.QDRANT_COLLECTION_NAME,
            collection_exists=collection_exists,
            indexed_points=indexed_points,
            source_directory=str(self.settings.rag_source_path),
            timestamp=datetime.now(timezone.utc),
        )

    async def index_documents(self, recreate_collection: bool = False) -> RagIndexResponse:
        self._validate_configuration()

        documents = self._load_source_documents()
        if not documents:
            raise NotFoundError("Knowledge base documents")

        chunks = self._chunk_documents(documents)
        if not chunks:
            raise BadRequestError("Knowledge base documents could not be chunked.")

        await self._ensure_collection(recreate_collection=recreate_collection)
        vectors = await self._embed_texts([chunk.text for chunk in chunks])

        points = [
            qdrant_models.PointStruct(
                id=str(uuid5(NAMESPACE_URL, f"{chunk.source}:{chunk.chunk_index}")),
                vector=vector,
                payload={
                    "doc_id": chunk.doc_id,
                    "source": chunk.source,
                    "title": chunk.title,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                },
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]

        try:
            await self.qdrant_client.upsert(
                collection_name=self.settings.QDRANT_COLLECTION_NAME,
                points=points,
                wait=True,
            )
        except Exception as exc:
            raise ServiceUnavailableError("Qdrant") from exc

        return RagIndexResponse(
            collection_name=self.settings.QDRANT_COLLECTION_NAME,
            source_directory=str(self.settings.rag_source_path),
            documents_indexed=len(documents),
            chunks_indexed=len(chunks),
        )

    async def query(self, request: RagQueryRequest) -> RagQueryResponse:
        self._validate_configuration()
        await self._ensure_collection_has_points()

        query_vector = (await self._embed_texts([request.question]))[0]

        try:
            hits = await self.qdrant_client.search(
                collection_name=self.settings.QDRANT_COLLECTION_NAME,
                query_vector=query_vector,
                limit=request.top_k,
                with_payload=True,
            )
        except Exception as exc:
            raise ServiceUnavailableError("Qdrant") from exc

        if not hits:
            raise NotFoundError("Indexed RAG documents")

        sources = [
            RagSourceChunk(
                doc_id=str(hit.payload.get("doc_id", "")),
                source=str(hit.payload.get("source", "")),
                title=str(hit.payload.get("title", "")),
                chunk_index=int(hit.payload.get("chunk_index", 0)),
                text=str(hit.payload.get("text", "")),
                score=float(hit.score) if hit.score is not None else None,
            )
            for hit in hits
        ]

        prompt = self._build_context_prompt(request.question, sources)
        answer = await self._generate_answer(
            prompt=prompt,
            model=request.model or self.settings.OLLAMA_MODEL_NAME,
            max_tokens=request.max_tokens or self.settings.OLLAMA_MAX_TOKENS,
            temperature=(
                request.temperature
                if request.temperature is not None
                else self.settings.OLLAMA_TEMPERATURE
            ),
        )

        return RagQueryResponse(
            model=answer["model"],
            answer=answer["content"],
            collection_name=self.settings.QDRANT_COLLECTION_NAME,
            sources=sources,
        )

    def _validate_configuration(self) -> None:
        if not self.settings.OLLAMA_EMBED_MODEL.strip():
            raise ConfigurationError("OLLAMA_EMBED_MODEL must not be empty.")
        if not self.settings.QDRANT_URL.strip():
            raise ConfigurationError("QDRANT_URL must not be empty.")
        if self.settings.QDRANT_VECTOR_SIZE <= 0:
            raise ConfigurationError("QDRANT_VECTOR_SIZE must be greater than zero.")
        if self.settings.RAG_CHUNK_OVERLAP >= self.settings.RAG_CHUNK_SIZE:
            raise ConfigurationError("RAG_CHUNK_OVERLAP must be smaller than RAG_CHUNK_SIZE.")

    def _load_source_documents(self) -> list[SourceDocument]:
        source_dir = self.settings.rag_source_path
        if not source_dir.exists():
            raise NotFoundError("Knowledge base directory", source_dir)

        documents: list[SourceDocument] = []
        for file_path in sorted(source_dir.rglob("*")):
            if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_DOCUMENT_SUFFIXES:
                continue

            text = file_path.read_text(encoding="utf-8").strip()
            if not text:
                continue

            relative_path = file_path.relative_to(source_dir).as_posix()
            documents.append(
                SourceDocument(
                    doc_id=relative_path,
                    source=relative_path,
                    title=file_path.stem,
                    text=text,
                )
            )

        return documents

    def _chunk_documents(self, documents: list[SourceDocument]) -> list[DocumentChunk]:
        chunk_size = self.settings.RAG_CHUNK_SIZE
        overlap = self.settings.RAG_CHUNK_OVERLAP
        step = chunk_size - overlap
        chunks: list[DocumentChunk] = []

        for document in documents:
            normalized = " ".join(document.text.split())
            start = 0
            chunk_index = 0

            while start < len(normalized):
                chunk_text = normalized[start : start + chunk_size].strip()
                if not chunk_text:
                    break

                chunks.append(
                    DocumentChunk(
                        doc_id=document.doc_id,
                        source=document.source,
                        title=document.title,
                        chunk_index=chunk_index,
                        text=chunk_text,
                    )
                )
                chunk_index += 1
                start += step

        return chunks

    async def _ensure_collection(self, recreate_collection: bool) -> None:
        try:
            collection_exists = await self.qdrant_client.collection_exists(
                collection_name=self.settings.QDRANT_COLLECTION_NAME
            )

            if collection_exists and recreate_collection:
                await self.qdrant_client.delete_collection(
                    collection_name=self.settings.QDRANT_COLLECTION_NAME
                )
                collection_exists = False

            if not collection_exists:
                await self.qdrant_client.create_collection(
                    collection_name=self.settings.QDRANT_COLLECTION_NAME,
                    vectors_config=qdrant_models.VectorParams(
                        size=self.settings.QDRANT_VECTOR_SIZE,
                        distance=self._distance_value(self.settings.QDRANT_DISTANCE),
                    ),
                )
        except Exception as exc:
            raise ServiceUnavailableError("Qdrant") from exc

    async def _ensure_collection_has_points(self) -> None:
        try:
            collection_exists = await self.qdrant_client.collection_exists(
                collection_name=self.settings.QDRANT_COLLECTION_NAME
            )
            if not collection_exists:
                raise NotFoundError("RAG collection", self.settings.QDRANT_COLLECTION_NAME)

            count_result = await self.qdrant_client.count(
                collection_name=self.settings.QDRANT_COLLECTION_NAME,
                exact=True,
            )
        except NotFoundError:
            raise
        except Exception as exc:
            raise ServiceUnavailableError("Qdrant") from exc

        if count_result.count == 0:
            raise NotFoundError("Indexed RAG documents")

    async def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for text in texts:
                    response = await client.post(
                        f"{self.base_url}/api/embeddings",
                        json={
                            "model": self.settings.OLLAMA_EMBED_MODEL,
                            "prompt": text,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    vector = data.get("embedding")
                    if not isinstance(vector, list):
                        raise BadRequestError("Ollama embedding response is invalid.")
                    if len(vector) != self.settings.QDRANT_VECTOR_SIZE:
                        raise ConfigurationError(
                            "Embedding vector size does not match QDRANT_VECTOR_SIZE."
                        )
                    vectors.append([float(value) for value in vector])
        except (BadRequestError, ConfigurationError):
            raise
        except httpx.HTTPStatusError as exc:
            detail = "Ollama embedding request failed."
            try:
                detail = exc.response.json().get("error", detail)
            except ValueError:
                pass
            if exc.response.status_code in {400, 404}:
                raise BadRequestError(detail) from exc
            raise ServiceUnavailableError("Ollama") from exc
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError("Ollama") from exc

        return vectors

    async def _generate_answer(
        self,
        *,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> dict[str, str]:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You answer using only the provided context. "
                        "If the context is insufficient, say so clearly."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = "Ollama chat request failed."
            try:
                detail = exc.response.json().get("error", detail)
            except ValueError:
                pass
            if exc.response.status_code in {400, 404}:
                raise BadRequestError(detail) from exc
            raise ServiceUnavailableError("Ollama") from exc
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError("Ollama") from exc

        data = response.json()
        message = data.get("message", {})
        return {
            "model": str(data.get("model", model)),
            "content": str(message.get("content", "")),
        }

    async def _check_ollama_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
            return True
        except httpx.HTTPError:
            return False

    async def _check_qdrant_health(self) -> bool:
        try:
            await self.qdrant_client.get_collections()
            return True
        except Exception:
            return False

    def _distance_value(self, configured_distance: str) -> qdrant_models.Distance:
        try:
            return qdrant_models.Distance[configured_distance.upper()]
        except KeyError as exc:
            raise ConfigurationError(
                f"Unsupported QDRANT_DISTANCE '{configured_distance}'."
            ) from exc

    def _build_context_prompt(self, question: str, sources: list[RagSourceChunk]) -> str:
        formatted_context = "\n\n".join(
            (
                f"[Source {index}] {source.title} ({source.source})\n"
                f"{source.text}"
            )
            for index, source in enumerate(sources, start=1)
        )
        return (
            "Use the context below to answer the question.\n\n"
            f"Question: {question}\n\n"
            f"Context:\n{formatted_context}\n\n"
            "Answer in a concise way and cite the relevant source titles in prose."
        )
