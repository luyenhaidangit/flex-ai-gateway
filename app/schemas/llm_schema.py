from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., examples=["user"])
    content: str = Field(..., examples=["hello"])


class LlmChatRequest(BaseModel):
    messages: list[ChatMessage]
    max_tokens: int | None = Field(default=None, ge=1, le=2048)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    model: str | None = Field(default=None, examples=["qwen2.5:0.5b"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "messages": [{"role": "user", "content": "hello"}],
                    "max_tokens": 64,
                    "temperature": 0.2,
                    "model": "qwen2.5:0.5b",
                }
            ]
        }
    }


class LlmChatResponse(BaseModel):
    model: str
    content: str
    finish_reason: str | None = None
