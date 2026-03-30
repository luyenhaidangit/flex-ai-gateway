from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import SettingsDep
from app.database import get_db
from app.schemas import HealthResponse
from app.services.health_service import check_database_health
from app.services.health_service import check_llm_health
from app.services.health_service import check_qdrant_health

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Check database, Ollama, and Qdrant connectivity.",
)
async def health_check(settings: SettingsDep, db: AsyncSession = Depends(get_db)):
    db_healthy = await check_database_health(db)
    llm_healthy = await check_llm_health(settings)
    qdrant_healthy = await check_qdrant_health(settings)
    system_status = "healthy" if db_healthy and llm_healthy and qdrant_healthy else "degraded"

    return HealthResponse(
        status=system_status,
        database="connected" if db_healthy else "disconnected",
        llm="connected" if llm_healthy else "disconnected",
        qdrant="connected" if qdrant_healthy else "disconnected",
        timestamp=datetime.now(timezone.utc),
    )
