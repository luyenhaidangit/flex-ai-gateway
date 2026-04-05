from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import SettingsDep
from app.core.exceptions import BadRequestError
from app.core.exceptions import ConfigurationError
from app.core.exceptions import NotFoundError
from app.core.exceptions import ServiceUnavailableError
from app.schemas.rag_schema import RagIndexRequest
from app.schemas.rag_schema import RagIndexResponse
from app.schemas.rag_schema import RagQueryRequest
from app.schemas.rag_schema import RagQueryResponse
from app.services.rag_service import RagService

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post(
    "/index",
    response_model=RagIndexResponse,
    summary="Index knowledge-base documents into Qdrant",
)
async def index_documents(request: RagIndexRequest, settings: SettingsDep):
    service = RagService(settings)

    try:
        return await service.index_documents(recreate_collection=request.recreate_collection)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except (BadRequestError, ConfigurationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except ServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc


@router.post(
    "/query",
    response_model=RagQueryResponse,
    summary="Query indexed knowledge-base documents",
)
async def query_documents(request: RagQueryRequest, settings: SettingsDep):
    service = RagService(settings)

    try:
        return await service.query(request)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except (BadRequestError, ConfigurationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except ServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc
