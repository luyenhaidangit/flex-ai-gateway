from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas import HealthResponse
from app.services.core import check_database_health, ml_model

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service and model health check",
    description="Check database connectivity and whether the ML model is fully loaded in memory.",
)
async def health_check(db: AsyncSession = Depends(get_db)):
    db_healthy = await check_database_health(db)
    model_loaded = ml_model.is_loaded

    system_status = (
        "healthy"
        if db_healthy and model_loaded
        else "initializing"
        if not model_loaded
        else "degraded"
    )

    return HealthResponse(
        status=system_status,
        database="connected" if db_healthy else "disconnected",
        model_loaded=model_loaded,
        timestamp=datetime.now(timezone.utc),
    )
