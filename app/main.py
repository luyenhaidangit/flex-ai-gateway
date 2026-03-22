from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.bootstraps.app import create_application
from app.database import init_db
from app.services.core import ml_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables and load ML model."""
    await init_db()
    await ml_model.load_model()
    yield


app = create_application(lifespan)
