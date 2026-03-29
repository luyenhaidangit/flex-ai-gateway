# Flex AI Gateway

`Flex AI Gateway` la FastAPI service cung cap API tra cuu suc khoe he thong va goi y dau tu cho securities dua tren du lieu bang `SECURITIES_INFO` trong Oracle Database.

## Chuc nang hien tai

- `GET /health`: kiem tra ket noi database
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
|   `-- securities.py
|-- services/
|   |-- health_service.py
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
- `ALLOWED_ORIGINS`: danh sach origin CORS
- `APP_TITLE`, `APP_DESCRIPTION`, `APP_VERSION`: metadata cua API neu ban muon bo sung trong `.env`

## Cai dat local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -e .
```

## Chay local

Dam bao Ollama dang chay va `.env` co:

```env
OLLAMA_BASE_URL=http://localhost:11434
```

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Sau khi chay:

- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- Securities advice: `http://localhost:8000/securities/advice/AAPL`

## Chay bang Docker

Neu chay bang Docker va gateway nam cung Docker network voi service `ollama`, dung:

```env
OLLAMA_BASE_URL=http://ollama:11434
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
- API goi y dau tu hien dung heuristic don gian dua tren `CHANGE_PERCENT` cua ban ghi moi nhat theo `symbol`
- ORM model map bang Oracle nam o `app/models/securities_info.py`
