from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.qa import LLMConfig


class QuestionGenerateRequest(BaseModel):
    scope: str = ""
    question_type: str = "选择题"
    difficulty: str = "中等"
    count: int = Field(default=5, ge=1, le=20)
    with_answer: bool = True
    llm_config: Optional[LLMConfig] = None


class QuestionGenerateResponse(BaseModel):
    questions: list[dict[str, Any]]
    sources: list[dict[str, Any]]
    raw: Optional[str] = None


class QuestionRecordOut(BaseModel):
    id: int
    course_id: int
    question_type: str
    difficulty: str
    question_content: str
    answer: Optional[str] = ""
    analysis: Optional[str] = ""
    knowledge_point: Optional[str] = ""
    sources: list[dict[str, Any]] = []
    created_at: str


class QuestionBatchDeleteRequest(BaseModel):
    ids: list[int]


class QuestionDeleteResponse(BaseModel):
    deleted: int
