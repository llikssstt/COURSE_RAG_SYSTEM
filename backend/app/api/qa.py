from fastapi import APIRouter

from app.schemas.qa import QARequest, QAResponse
from app.services import qa_service

router = APIRouter(prefix="/courses/{course_id}/qa", tags=["qa"])


@router.post("", response_model=QAResponse)
def ask_course_question(course_id: int, payload: QARequest):
    llm_config = payload.llm_config.model_dump() if payload.llm_config else None
    return qa_service.ask(course_id, payload.question, payload.top_k, llm_config)


@router.get("/history")
def get_qa_history(course_id: int):
    return qa_service.history(course_id)
