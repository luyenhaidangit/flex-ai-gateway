# app/core/config.py

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # =========================
    # APP
    # =========================
    APP_TITLE: str = "Flex AI Gateway"
    APP_DESCRIPTION: str = "Flex AI Gateway Project"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # =========================
    # DATABASE (Oracle)
    # =========================
    DATABASE_URL: str = "oracle+oracledb://ai_gateway:SecurePass123@db:1521/?service_name=XEPDB1"
    ORACLE_WALLET_DIR: str | None = None
    ORACLE_WALLET_PASSWORD: str | None = None

    # =========================
    # LLM / OLLAMA
    # =========================
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL_NAME: str = "qwen2.5:0.5b"
    OLLAMA_TIMEOUT_SECONDS: float = 120.0
    OLLAMA_MAX_TOKENS: int = 256
    OLLAMA_TEMPERATURE: float = 0.2

    # =========================
    # ML MODEL
    # =========================
    MODEL_NAME: str = "sentiment-analysis-v1"
    CONFIDENCE_THRESHOLD: float = 0.5

    # =========================
    # SECURITY
    # =========================
    SECRET_KEY: str = "CHANGE_ME"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # =========================
    # CORS
    # =========================
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # =========================
    # LOGGING
    # =========================
    LOG_LEVEL: str = "INFO"

    # =========================
    # REDIS
    # =========================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()