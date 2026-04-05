from fastapi.testclient import TestClient

from app.bootstrap.factory import create_application
from app.routers import rag as rag_router_module
from app.schemas.rag_schema import RagIndexResponse
from app.schemas.rag_schema import RagQueryResponse
from app.schemas.rag_schema import RagSourceChunk


class FakeRagService:
    def __init__(self, settings):
        self.settings = settings

    async def index_documents(self, recreate_collection: bool = False):
        return RagIndexResponse(
            collection_name="rag_documents",
            source_directory="docs/knowledge-base",
            documents_indexed=1,
            chunks_indexed=2,
        )

    async def query(self, request):
        return RagQueryResponse(
            model="qwen2.5:1.5b",
            answer=f"Answer for: {request.question}",
            collection_name="rag_documents",
            sources=[
                RagSourceChunk(
                    doc_id="doc-1",
                    source="sample.md",
                    title="Sample",
                    chunk_index=0,
                    text="Qdrant stores vectors.",
                    score=0.92,
                )
            ],
        )


def test_rag_endpoints(monkeypatch):
    monkeypatch.setattr(rag_router_module, "RagService", FakeRagService)
    client = TestClient(create_application())

    index_response = client.post("/rag/index", json={"recreate_collection": True})
    assert index_response.status_code == 200
    assert index_response.json()["chunks_indexed"] == 2

    query_response = client.post("/rag/query", json={"question": "Qdrant de lam gi?"})
    assert query_response.status_code == 200
    body = query_response.json()
    assert body["collection_name"] == "rag_documents"
    assert body["sources"][0]["title"] == "Sample"
