from fastapi import FastAPI

from app.bootstrap.metadata import APP_DESCRIPTION
from app.bootstrap.metadata import APP_TITLE
from app.bootstrap.metadata import APP_VERSION
from app.bootstrap.middleware import register_middleware
from app.bootstrap.routes import register_routes
from app.config import get_settings


def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    register_middleware(app, settings)
    register_routes(app)

    return app
