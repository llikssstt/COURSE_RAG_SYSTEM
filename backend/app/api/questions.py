from fastapi import APIRouter

from app.schemas.question import QuestionGenerateRequest, QuestionGenerateResponse, QuestionRecordOut
from app.services import question_service

router = APIRouter(prefix="/courses/{course_id}/questions", tags=["questions"])


@router.post("/generate", response_model=QuestionGenerateResponse)
def generate_questions(course_id: int, payload: QuestionGenerateRequest):
    return question_service.generate(course_id, payload.model_dump())


@router.get("/history", response_model=list[QuestionRecordOut])
def get_question_history(course_id: int):
    return question_service.history(course_id)
