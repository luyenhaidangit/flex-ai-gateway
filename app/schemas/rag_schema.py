from pydantic import BaseModel, Field


class RagIndexRequest(BaseModel):
    recreate_collection: bool = Field(
        default=False,
        description="Delete and recreate the collection before indexing.",
    )


class RagIndexResponse(BaseModel):
    collection_name: str
    source_directory: str
    documents_indexed: int
    chunks_indexed: int


class RagSourceChunk(BaseModel):
    doc_id: str
    source: str
    title: str
    chunk_index: int
    text: str
    score: float | None = None


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, examples=["Qdrant duoc dung de lam gi?"])
    top_k: int = Field(default=5, ge=1, le=10)
    max_tokens: int | None = Field(default=None, ge=1, le=2048)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    model: str | None = Field(default=None, examples=["qwen2.5:1.5b"])


class RagQueryResponse(BaseModel):
    model: str
    answer: str
    collection_name: str
    sources: list[RagSourceChunk]
