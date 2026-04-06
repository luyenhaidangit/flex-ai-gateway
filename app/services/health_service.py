import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.logging import get_logger


logger = get_logger(__name__)


async def check_database_health(db: AsyncSession) -> bool:
    try:
        await db.execute(text("SELECT 1 FROM DUAL"))
        return True
    except Exception:
        return False


async def check_llm_health(settings: Settings) -> bool:
    base_url = settings.OLLAMA_BASE_URL.rstrip("/")
    verify = settings.ollama_http_verify

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0), verify=verify) as client:
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
        return True
    except httpx.HTTPError:
        return False


async def check_qdrant_health(settings: Settings) -> bool:
    base_url = settings.QDRANT_URL.rstrip("/")
    verify = settings.qdrant_http_verify

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0), verify=verify) as client:
            response = await client.get(f"{base_url}/collections")
            response.raise_for_status()
        return True
    except Exception as exc:
        logger.warning(
            "Qdrant health check failed",
            qdrant_url=settings.QDRANT_URL,
            error_type=type(exc).__name__,
            error=str(exc),
        )
        return False
