# Flex AI Gateway

`Flex AI Gateway` la FastAPI service cung cap API suc khoe he thong, LLM chat, securities advice, va RAG cho tai lieu tinh bang Qdrant + Ollama.

## Chuc nang hien tai

- `GET /health`: kiem tra ket noi database, Ollama, va Qdrant
- `GET /rag/health`: kiem tra rieng tinh trang RAG stack
- `POST /rag/index`: nap tai lieu tu `docs/knowledge-base` vao Qdrant
- `POST /rag/query`: hoi dap tren knowledge base da index
- `GET /securities/advice/{symbol}`: lay goi y dau tu cho ma chung khoan, vi du `AAPL`
- `POST /securities/price-change`: them thong tin bien dong gia moi
- Swagger UI tai `http://localhost:8000/docs`

## Cong nghe su dung

- Python `3.11+`
- FastAPI
- Uvicorn
- SQLAlchemy `2.x`
- OracleDB driver `oracledb`
- Pydantic Settings
- Docker
- Qdrant

## Cau truc thu muc chinh

```text
app/
|-- main.py
|-- bootstrap/
|   |-- factory.py
|   |-- middleware.py
|   `-- routes.py
|-- core/
|   `-- config.py
|-- routers/
|   |-- health.py
|   |-- rag.py
|   `-- securities.py
|-- services/
|   |-- health_service.py
|   |-- rag_service.py
|   `-- securities_service.py
|-- repositories/
|   `-- securities_repository.py
|-- models/
|   `-- securities_info.py
|-- schemas/
|   |-- common_schema.py
|   |-- health_schema.py
|   `-- securities_schema.py
|-- database.py
```

## Yeu cau moi truong

- Python `3.11+`
- Oracle Database co bang `SECURITIES_INFO`
- File `.env` hop le
- Ollama co chat model va embedding model da pull
- Qdrant neu muon dung RAG

## Cau hinh

Tao file `.env` tu mau:

```powershell
Copy-Item .env.example .env
```

Cac bien quan trong:

- `DATABASE_URL`: chuoi ket noi Oracle
- `ORACLE_WALLET_DIR`: thu muc wallet neu dung Oracle Wallet
- `ORACLE_WALLET_PASSWORD`: mat khau wallet neu co
- `OLLAMA_BASE_URL`: URL Ollama. Chay local bang `uvicorn` thi dung `http://localhost:11434`; chay trong Docker Compose cung network voi service `ollama` thi dung `http://ollama:11434`
- `OLLAMA_MODEL_NAME`: chat model, mac dinh `qwen2.5:1.5b`
- `OLLAMA_EMBED_MODEL`: embedding model, mac dinh `nomic-embed-text-v2-moe`
- `QDRANT_URL`: URL Qdrant
- `QDRANT_COLLECTION_NAME`: ten collection vector store
- `QDRANT_VECTOR_SIZE`: kich thuoc vector embedding, mac dinh `768`
- `QDRANT_DISTANCE`: metric cua Qdrant, mac dinh `Cosine`
- `RAG_SOURCE_DIR`: thu muc nguon tai lieu, mac dinh `docs/knowledge-base`
- `ALLOWED_ORIGINS`: danh sach origin CORS
- `APP_TITLE`, `APP_DESCRIPTION`, `APP_VERSION`: metadata cua API neu ban muon bo sung trong `.env`

## Cai dat local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -e .
```

Neu muon chay test:

```powershell
pip install -e .[dev]
```

## Chay local

Dam bao Ollama dang chay, da pull du 2 model, va `.env` co:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=qwen2.5:1.5b
OLLAMA_EMBED_MODEL=nomic-embed-text-v2-moe
QDRANT_URL=http://localhost:6333
```

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Sau khi chay:

- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- RAG health: `http://localhost:8000/rag/health`
- Securities advice: `http://localhost:8000/securities/advice/AAPL`

## Chay bang Docker Compose local

Repo nay co compose rieng de dev doc lap:

```powershell
docker compose up -d
```

Lenh nay se chay:

- `qdrant`
- `ollama`
- `ollama-init` de pull `qwen2.5:1.5b` va `nomic-embed-text-v2-moe`
- `ai-gateway`

## Chay bang Docker image

Neu chay bang Docker va gateway nam cung Docker network voi service `ollama`, dung:

```env
OLLAMA_BASE_URL=http://ollama:11434
QDRANT_URL=http://qdrant:6333
```

```powershell
docker build -t ai-gateway .
docker run --rm -p 8000:8000 --env-file .env ai-gateway
```

## Test nhanh API

### Health check

```powershell
curl http://localhost:8000/health
```

### RAG health

```powershell
curl http://localhost:8000/rag/health
```

### Index knowledge base

```powershell
curl -X POST http://localhost:8000/rag/index `
  -H "Content-Type: application/json" `
  -d '{"recreate_collection":true}'
```

### Query knowledge base

```powershell
curl -X POST http://localhost:8000/rag/query `
  -H "Content-Type: application/json" `
  -d '{"question":"Qdrant dung de lam gi?","top_k":3}'
```

### Securities advice

```powershell
curl http://localhost:8000/securities/advice/AAPL
```

Response mau:

```json
{
  "symbol": "AAPL",
  "recommendation": "BUY",
  "confidence": 0.78
}
```

### Them bien dong gia

```powershell
curl -X POST http://localhost:8000/securities/price-change `
  -H "Content-Type: application/json" `
  -d '{"symbol":"AAPL","trade_time":"2026-03-23T09:45:00","price":186.2,"volume":2500000,"change_percent":0.49}'
```

## Ghi chu

- Entry point runtime la `app.main:app`
- Knowledge base mac dinh nam o `docs/knowledge-base`
- RAG hien ho tro file `.md` va `.txt`
- API goi y dau tu hien dung heuristic don gian dua tren `CHANGE_PERCENT` cua ban ghi moi nhat theo `symbol`
- ORM model map bang Oracle nam o `app/models/securities_info.py`
