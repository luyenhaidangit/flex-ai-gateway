from pydantic import BaseModel, Field
from datetime import datetime


# ─── Request Models ───────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request body for POST /api/chat."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The prompt to send to the AI model",
        examples=["Explain what is Docker in 2 sentences"],
    )
    model: str = Field(
        default="gpt-3.5-turbo",
        description="AI model to use",
        examples=["gpt-3.5-turbo", "gpt-4"],
    )
    max_tokens: int = Field(
        default=500,
        ge=1,
        le=4000,
        description="Maximum tokens in the response",
    )


# ─── Response Models ──────────────────────────────────────────

class ChatResponse(BaseModel):
    """Response body for chat endpoints."""

    id: int
    prompt: str
    response: str
    model: str
    cached: bool = Field(description="Whether this response was served from cache")
    created_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str = Field(examples=["healthy"])
    database: str = Field(examples=["connected"])
    timestamp: datetime


class ErrorDetail(BaseModel):
    """Standard error response."""

    detail: str
