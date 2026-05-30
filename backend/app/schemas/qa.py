from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.core.settings import settings


class LLMConfig(BaseModel):
    api_key: str = ""
    base_url: str = settings.default_base_url
    model: str = settings.default_chat_model


class QARequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)
    llm_config: Optional[LLMConfig] = None


class QAResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]] = []
    retrieval_mode: Optional[str] = None
    route_type: Optional[str] = None
    retrieval_query: Optional[str] = None
