# AVOIDANCE_TABLE — Proof of Avoiding Common Mistakes

Tôi đã tránh đủ **8/8 lỗi** phổ biến trong bảng lỗi buổi 1. Dưới đây là chi tiết cách xử lý từng lỗi:

---

## ✅ Lỗi #1 — Base image `python:latest`

**Cách xử lý:** Sử dụng `python:3.11-slim` với multi-stage build. Stage builder cài dependencies, stage runtime chỉ copy kết quả → image cuối gọn nhẹ ~200MB.

```dockerfile
FROM python:3.11-slim AS builder
# ... install deps ...
FROM python:3.11-slim
COPY --from=builder /install /usr/local
```

---

## ✅ Lỗi #2 — Không có `.dockerignore`

**Cách xử lý:** Tạo `.dockerignore` với 12 dòng ignore, loại bỏ `__pycache__/`, `.git/`, `.venv/`, `*.pyc`, `.env`, `utils/`, `docker/` khỏi build context.

```
__pycache__/
*.pyc
*.pyo
.git/
.gitignore
.venv/
*.egg-info/
.env
utils/
*.md
!README.md
docker/
```

---

## ✅ Lỗi #3 — Hardcode connection string / password

**Cách xử lý:** Toàn bộ secrets đọc từ environment variables qua Pydantic Settings. `DATABASE_URL`, `AI_API_KEY` inject qua `docker-compose.yml`. File `.env` nằm trong `.gitignore`.

```python
# app/config.py
class Settings(BaseSettings):
    DATABASE_URL: str = "..."
    AI_API_KEY: str = "sk-mock-key"
```

```yaml
# docker-compose.yml
environment:
  DATABASE_URL: "oracle+oracledb://${ORACLE_USER}:${ORACLE_PASSWORD}@db:1521/?service_name=XEPDB1"
```

---

## ✅ Lỗi #4 — Không có healthcheck cho DB

**Cách xử lý:** Oracle XE image có sẵn `healthcheck.sh`. Cấu hình `depends_on` với `condition: service_healthy` — API chỉ start sau khi DB sẵn sàng.

```yaml
db:
  healthcheck:
    test: ["CMD", "healthcheck.sh"]
    interval: 10s
    timeout: 5s
    retries: 10
    start_period: 30s

api:
  depends_on:
    db:
      condition: service_healthy
```

---

## ✅ Lỗi #5 — Nhét toàn bộ logic vào 1 file `main.py`

**Cách xử lý:** Tách code theo cấu trúc FastAPI best practice:

```
app/
├── main.py           # Khởi tạo app + middleware + routers
├── config.py         # Settings từ env vars
├── database.py       # SQLAlchemy async engine
├── routers/api.py    # 3 endpoints
├── models/schemas.py # Pydantic request/response
├── models/database.py# SQLAlchemy ORM models
└── services/core.py  # Business logic (cache, AI call)
```

---

## ✅ Lỗi #6 — Không dùng Pydantic validate input/output

**Cách xử lý:** Mọi endpoint đều dùng Pydantic `BaseModel` với validation:

```python
class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    model: str = Field(default="gpt-3.5-turbo")
    max_tokens: int = Field(default=500, ge=1, le=4000)
```

Input sai → FastAPI tự trả 422 với message chi tiết. Output cũng dùng `ChatResponse` model đảm bảo schema nhất quán.

---

## ✅ Lỗi #7 — CORS wildcard `allow_origins=["*"]`

**Cách xử lý:** CORS origins đọc từ env var `ALLOWED_ORIGINS`, chỉ cho phép domain cụ thể:

```python
# app/config.py
ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

@property
def cors_origins(self) -> list[str]:
    return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # NOT ["*"]
)
```

---

## ✅ Lỗi #8 — Chạy container với user root

**Cách xử lý:** Tạo user `aiuser` không phải root và chuyển sang user đó trước khi chạy app:

```dockerfile
RUN useradd -m -r aiuser && chown -R aiuser:aiuser /app
USER aiuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
