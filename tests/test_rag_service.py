from app.core.config import Settings
from app.core.exceptions import ConfigurationError
from app.schemas.rag_schema import RagSourceChunk
from app.services.rag_service import RagService


def build_settings(**overrides) -> Settings:
    values = {
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL_NAME": "qwen2.5:1.5b",
        "OLLAMA_EMBED_MODEL": "nomic-embed-text-v2-moe",
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION_NAME": "rag_documents",
        "QDRANT_VECTOR_SIZE": 768,
        "QDRANT_DISTANCE": "Cosine",
        "RAG_SOURCE_DIR": "docs/knowledge-base",
        "RAG_CHUNK_SIZE": 20,
        "RAG_CHUNK_OVERLAP": 5,
    }
    values.update(overrides)
    return Settings(**values)


def test_chunk_documents_splits_text_with_overlap():
    settings = build_settings()
    service = RagService(settings)
    documents = [service._load_source_documents()[0]]

    chunks = service._chunk_documents(documents)

    assert len(chunks) >= 2
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1


def test_build_context_prompt_includes_question_and_sources():
    settings = build_settings()
    service = RagService(settings)
    sources = [
        RagSourceChunk(
            doc_id="doc-1",
            source="sample.md",
            title="Sample",
            chunk_index=0,
            text="Qdrant stores vectors.",
            score=0.91,
        )
    ]

    prompt = service._build_context_prompt("Qdrant de lam gi?", sources)

    assert "Qdrant de lam gi?" in prompt
    assert "Qdrant stores vectors." in prompt
    assert "Sample" in prompt


def test_validate_configuration_rejects_empty_embedding_model():
    settings = build_settings(OLLAMA_EMBED_MODEL=" ")
    service = RagService(settings)

    try:
        service._validate_configuration()
    except ConfigurationError as exc:
        assert "OLLAMA_EMBED_MODEL" in exc.message
    else:
        raise AssertionError("ConfigurationError was not raised")
