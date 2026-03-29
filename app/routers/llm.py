from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import SettingsDep
from app.core.exceptions import BadRequestError
from app.core.exceptions import ServiceUnavailableError
from app.schemas.llm_schema import LlmChatRequest
from app.schemas.llm_schema import LlmChatResponse
from app.services.llm_service import LlmService

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post(
    "/chat",
    response_model=LlmChatResponse,
    summary="Send a chat request to the hosted LLM",
)
async def chat_with_model(request: LlmChatRequest, settings: SettingsDep):
    service = LlmService(settings)

    try:
        return await service.chat(request)
    except BadRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc
    except ServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service is currently unavailable",
        ) from exc
