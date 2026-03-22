from collections.abc import Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.config import get_settings
from app.routers.api import health_router
from app.routers.api import router as api_router


def create_application(lifespan: Callable) -> FastAPI:
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


def configure_middleware(app: FastAPI, settings: Settings) -> None:
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
