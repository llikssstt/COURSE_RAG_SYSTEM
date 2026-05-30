from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.qa import LLMConfig


class SummaryGenerateRequest(BaseModel):
    summary_type: str = "课程复习提纲"
    scope: str = ""
    top_k: int = Field(default=12, ge=1, le=30)
    llm_config: Optional[LLMConfig] = None


class SummaryGenerateResponse(BaseModel):
    summary: str
    sources: list[dict[str, Any]] = []
