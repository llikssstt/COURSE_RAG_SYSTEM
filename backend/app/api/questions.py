from fastapi import APIRouter

from app.schemas.question import (
    QuestionBatchDeleteRequest,
    QuestionDeleteResponse,
    QuestionGenerateRequest,
    QuestionGenerateResponse,
    QuestionRecordOut,
)
from app.services import question_service

router = APIRouter(prefix="/courses/{course_id}/questions", tags=["questions"])


@router.post("/generate", response_model=QuestionGenerateResponse)
def generate_questions(course_id: int, payload: QuestionGenerateRequest):
    return question_service.generate(course_id, payload.model_dump())


@router.get("/history", response_model=list[QuestionRecordOut])
def get_question_history(
    course_id: int,
    keyword: str = "",
    question_type: str = "",
    difficulty: str = "",
    limit: int = 100,
    offset: int = 0,
):
    return question_service.history(course_id, keyword, question_type, difficulty, limit, offset)


@router.get("/{question_id}", response_model=QuestionRecordOut)
def get_question_record(course_id: int, question_id: int):
    return question_service.get_record(course_id, question_id)


@router.delete("/{question_id}", response_model=QuestionDeleteResponse)
def delete_question_record(course_id: int, question_id: int):
    return question_service.delete_record(course_id, question_id)


@router.delete("", response_model=QuestionDeleteResponse)
def delete_question_records(course_id: int, payload: QuestionBatchDeleteRequest):
    return question_service.delete_records(course_id, payload.ids)
