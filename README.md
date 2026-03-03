# 🚀 AI Gateway — Proxy & Cache AI API Service

FastAPI service đóng vai trò **proxy & cache** cho các API AI bên thứ ba (OpenAI, Groq). Nhận request từ client, forward đến AI provider, cache kết quả vào **Oracle Database**, hỗ trợ truy vấn lại kết quả đã cache.

## 📋 Features

- **POST /api/chat** — Gửi prompt đến AI, tự động cache response (hash-based)
- **GET /api/chat/{id}** — Truy vấn kết quả đã cache theo ID
- **GET /health** — Healthcheck service + database connectivity
- **Pydantic validation** — Input/output schema rõ ràng, 422 error chi tiết
- **Swagger UI** — Tự động tại `/docs`
- **Docker production-ready** — Multi-stage build, non-root user, Oracle healthcheck

## 🏗️ Project Structure

```
ai-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + CORS + routers
│   ├── config.py             # Pydantic Settings (env vars)
│   ├── database.py           # SQLAlchemy async + Oracle
│   ├── routers/
│   │   └── api.py            # 3 API endpoints
│   ├── models/
│   │   ├── schemas.py        # Pydantic request/response
│   │   └── database.py       # SQLAlchemy ORM models
│   └── services/
│       └── core.py           # Business logic
├── docker/
│   ├── Dockerfile            # Multi-stage build
│   └── docker-compose.yml    # API + Oracle XE
├── AVOIDANCE_TABLE.md        # Proof tránh 8/8 lỗi
├── requirements.txt
├── .dockerignore
├── .env.example
└── .gitignore
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed

### Run

```bash
# Clone repo
git clone https://github.com/<your-username>/ai-gateway.git
cd ai-gateway

# (Optional) Copy and customize env vars
cp .env.example .env

# Start services
cd docker
docker-compose up --build -d

# Check status
docker-compose ps
```

### Test

```bash
# Health check
curl http://localhost:8000/health

# Send a prompt
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is Docker?", "model": "gpt-3.5-turbo"}'

# Get cached result
curl http://localhost:8000/api/chat/1

# Test validation (422 error)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Swagger UI

Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `oracle+oracledb://...` | Oracle connection string |
| `ORACLE_USER` | `ai_gateway` | Oracle app user |
| `ORACLE_PASSWORD` | `SecurePass123` | Oracle password |
| `AI_API_KEY` | `sk-mock-key` | AI provider API key |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | CORS allowed origins |

## 🛡️ Best Practices Applied

See [AVOIDANCE_TABLE.md](AVOIDANCE_TABLE.md) for detailed proof of avoiding all 8 common mistakes.
