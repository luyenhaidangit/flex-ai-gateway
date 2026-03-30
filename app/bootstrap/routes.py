from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.llm import router as llm_router
from app.routers.rag import router as rag_router
from app.routers.securities import router as securities_router


def register_routes(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(llm_router)
    app.include_router(rag_router)
    app.include_router(securities_router)
