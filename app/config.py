from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "oracle+oracledb://ai_gateway:SecurePass123@db:1521/?service_name=XEPDB1"
    ORACLE_WALLET_DIR: str | None = None

    # ML Model Config
    MODEL_NAME: str = "sentiment-analysis-v1"
    CONFIDENCE_THRESHOLD: float = 0.5

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
