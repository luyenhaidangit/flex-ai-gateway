# app/core/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # =========================
    # APP
    # =========================
    APP_NAME: str = "AI Gateway"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # =========================
    # DATABASE
    # =========================
    DB_HOST: str = "localhost"
    DB_PORT: int = 1521
    DB_USER: str = "system"
    DB_PASSWORD: str = "oracle"
    DB_NAME: str = "ORCLCDB"

    # Oracle connection string
    DATABASE_URL: str | None = None

    # =========================
    # SECURITY
    # =========================
    SECRET_KEY: str = "CHANGE_ME"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # =========================
    # LOGGING
    # =========================
    LOG_LEVEL: str = "INFO"

    # =========================
    # REDIS
    # =========================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()