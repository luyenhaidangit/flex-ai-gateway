from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas import ChatRequest, ChatResponse, HealthResponse, ErrorDetail
from app.services.core import (
    hash_prompt,
    get_cached_response,
    get_chat_by_id,
    save_to_cache,
    call_ai_api,
    check_database_health,
)

router = APIRouter(prefix="/api", tags=["AI Gateway"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a prompt to AI (with caching)",
    description=(
        "Receives a prompt, checks the cache for an existing response. "
        "If cached, returns immediately. Otherwise, calls the AI API, "
        "stores the result, and returns it."
    ),
    responses={
        422: {"model": ErrorDetail, "description": "Validation error"},
    },
)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    # Check cache first
    prompt_h = hash_prompt(request.prompt, request.model)
    cached = await get_cached_response(prompt_h, request.model, db)

    if cached:
        return ChatResponse(
            id=cached.id,
            prompt=cached.prompt,
            response=cached.response,
            model=cached.model,
            cached=True,
            created_at=cached.created_at,
        )

    # Cache miss — call AI API
    ai_response = await call_ai_api(
        prompt=request.prompt,
        model=request.model,
        max_tokens=request.max_tokens,
    )

    # Save to DB
    entry = await save_to_cache(
        prompt=request.prompt,
        response=ai_response,
        model=request.model,
        prompt_hash=prompt_h,
        db=db,
    )

    return ChatResponse(
        id=entry.id,
        prompt=entry.prompt,
        response=entry.response,
        model=entry.model,
        cached=False,
        created_at=entry.created_at,
    )


@router.get(
    "/chat/{chat_id}",
    response_model=ChatResponse,
    summary="Get cached chat result by ID",
    description="Retrieve a previously cached AI chat response by its ID.",
    responses={
        404: {"model": ErrorDetail, "description": "Chat not found"},
    },
)
async def get_chat(chat_id: int, db: AsyncSession = Depends(get_db)):
    entry = await get_chat_by_id(chat_id, db)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat with id {chat_id} not found",
        )

    return ChatResponse(
        id=entry.id,
        prompt=entry.prompt,
        response=entry.response,
        model=entry.model,
        cached=True,
        created_at=entry.created_at,
    )


# ─── Health Check (outside /api prefix) ──────────────────────

health_router = APIRouter(tags=["Health"])


@health_router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns service status and database connectivity.",
)
async def health_check(db: AsyncSession = Depends(get_db)):
    db_healthy = await check_database_health(db)

    return HealthResponse(
        status="healthy" if db_healthy else "unhealthy",
        database="connected" if db_healthy else "disconnected",
        timestamp=datetime.now(timezone.utc),
    )
