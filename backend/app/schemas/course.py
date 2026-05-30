from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class CourseCreate(BaseModel):
    name: str
    description: str = ""


class CourseOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""
    created_at: str


class CourseStats(BaseModel):
    course_id: int
    document_count: int
    chunk_count: int
    qa_count: int
    question_count: int
    wrong_question_count: int = 0
