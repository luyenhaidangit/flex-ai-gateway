from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers.api import health_router
from app.routers.api import router as api_router
from app.services.core import ml_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables and load ML model."""
    await init_db()
    await ml_model.load_model()
    yield


def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="MLOps Inference Server",
        description=(
            "Production-ready FastAPI service for ML Model Inference. "
            "Loads a simulated classification model into RAM during startup, "
            "provides inference endpoints powered by uvicorn workers, "
            "and logs all predictions to Oracle Database."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    configure_middleware(app, settings)
    configure_routes(app)

    return app


def configure_middleware(app: FastAPI, settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )


def configure_routes(app: FastAPI) -> None:
    app.include_router(api_router)
    app.include_router(health_router)


app = create_application()
