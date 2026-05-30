from __future__ import annotations

from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class WrongQuestionCreate(BaseModel):
    question_id: Optional[int] = None
    source_type: str = "manual"
    question_type: str = ""
    difficulty: str = ""
    question_content: str
    user_answer: str = ""
    correct_answer: str = ""
    analysis: str = ""
    knowledge_point: str = ""
    sources: Union[list[dict[str, Any]], str] = []
    note: str = ""


class WrongQuestionUpdate(BaseModel):
    note: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(未掌握|已掌握)$")
    user_answer: Optional[str] = None


class WrongQuestionOut(BaseModel):
    id: int
    course_id: int
    question_id: Optional[int] = None
    source_type: str
    question_type: Optional[str] = ""
    difficulty: Optional[str] = ""
    question_content: str
    user_answer: Optional[str] = ""
    correct_answer: Optional[str] = ""
    analysis: Optional[str] = ""
    knowledge_point: Optional[str] = ""
    sources: list[dict[str, Any]] = []
    note: Optional[str] = ""
    status: str
    review_count: int
    last_reviewed_at: Optional[str] = None
    created_at: str
    updated_at: str


class WrongQuestionBatchDeleteRequest(BaseModel):
    ids: list[int]


class WrongQuestionDeleteResponse(BaseModel):
    deleted: int
