import httpx

from app.core.exceptions import BadRequestError
from app.core.config import Settings
from app.core.exceptions import ServiceUnavailableError
from app.schemas.llm_schema import LlmChatRequest
from app.schemas.llm_schema import LlmChatResponse


class LlmService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def chat(self, request: LlmChatRequest) -> LlmChatResponse:
        payload = {
            "model": request.model or self.settings.OLLAMA_MODEL_NAME,
            "messages": [message.model_dump() for message in request.messages],
            "stream": False,
            "options": {
                "temperature": (
                    request.temperature
                    if request.temperature is not None
                    else self.settings.OLLAMA_TEMPERATURE
                ),
                "num_predict": request.max_tokens or self.settings.OLLAMA_MAX_TOKENS,
            },
        }

        base_url = self.settings.OLLAMA_BASE_URL.rstrip("/")
        timeout = httpx.Timeout(self.settings.OLLAMA_TIMEOUT_SECONDS)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(f"{base_url}/api/chat", json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = "Ollama request failed."
            try:
                data = exc.response.json()
                detail = data.get("error", detail)
            except ValueError:
                pass

            if exc.response.status_code in {400, 404}:
                raise BadRequestError(detail) from exc

            raise ServiceUnavailableError("Ollama") from exc
        except httpx.HTTPError as exc:
            raise ServiceUnavailableError("Ollama") from exc

        data = response.json()
        message = data.get("message", {})

        return LlmChatResponse(
            model=data.get("model", payload["model"]),
            content=message.get("content", ""),
            finish_reason="stop" if data.get("done") else None,
        )

    async def is_healthy(self) -> bool:
        base_url = self.settings.OLLAMA_BASE_URL.rstrip("/")
        timeout = httpx.Timeout(10.0)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(f"{base_url}/api/tags")
                response.raise_for_status()
            return True
        except httpx.HTTPError:
            return False
