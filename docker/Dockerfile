# ──────────────────────────────────────────────
# Stage 1: Builder — install dependencies
# ──────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system dependencies for oracledb
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libaio1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ──────────────────────────────────────────────
# Stage 2: Runtime — lean production image
# ──────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependency for Oracle client
RUN apt-get update && \
    apt-get install -y --no-install-recommends libaio1 && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root user (Lỗi #8)
RUN useradd -m -r aiuser && chown -R aiuser:aiuser /app

# Copy application code
COPY app/ ./app/

# Switch to non-root user
USER aiuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
