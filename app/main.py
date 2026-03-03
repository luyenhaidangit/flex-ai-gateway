from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers.api import router as api_router, health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables. Shutdown: cleanup."""
    await init_db()
    yield


settings = get_settings()

app = FastAPI(
    title="AI Gateway",
    description=(
        "Proxy & Cache service for third-party AI APIs. "
        "Receives prompts, caches responses in Oracle DB, "
        "and serves cached results for repeated queries."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — specific origins only, NOT wildcard "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)
app.include_router(health_router)
