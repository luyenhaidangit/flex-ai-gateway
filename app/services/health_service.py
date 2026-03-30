import httpx
from qdrant_client import AsyncQdrantClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings


async def check_database_health(db: AsyncSession) -> bool:
    try:
        await db.execute(text("SELECT 1 FROM DUAL"))
        return True
    except Exception:
        return False


async def check_llm_health(settings: Settings) -> bool:
    base_url = settings.OLLAMA_BASE_URL.rstrip("/")

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
        return True
    except httpx.HTTPError:
        return False


async def check_qdrant_health(settings: Settings) -> bool:
    try:
        client = AsyncQdrantClient(url=settings.QDRANT_URL, timeout=10.0)
        await client.get_collections()
        return True
    except Exception:
        return False
