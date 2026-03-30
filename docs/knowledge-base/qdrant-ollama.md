# Qdrant va Ollama

Qdrant la vector database dung de luu embedding va tim kiem semantic search.

Ollama cung cap local model serving cho ca chat model va embedding model. Trong moi truong nay:

- Chat model mac dinh la `qwen2.5:1.5b`
- Embedding model mac dinh la `nomic-embed-text-v2-moe`

Luong RAG co ban:

1. Gateway doc tai lieu tu thu muc `docs/knowledge-base`
2. Tai lieu duoc chia thanh cac chunk nho co overlap
3. Moi chunk duoc embedding bang Ollama
4. Vector duoc upsert vao Qdrant collection `rag_documents`
5. Khi nguoi dung hoi, gateway embedding cau hoi, tim `top_k` chunk lien quan trong Qdrant, roi gui context vao chat model

Qdrant va Ollama nen chay cung Docker network voi `flex-ai-gateway` de dung hostname noi bo `qdrant` va `ollama`.
