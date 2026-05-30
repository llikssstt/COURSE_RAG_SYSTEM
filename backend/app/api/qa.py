from fastapi import APIRouter

from app.schemas.qa import BatchDeleteRequest, DeleteResponse, QAHistoryOut, QARequest, QAResponse
from app.services import qa_service

router = APIRouter(prefix="/courses/{course_id}/qa", tags=["qa"])


@router.post("", response_model=QAResponse)
def ask_course_question(course_id: int, payload: QARequest):
    llm_config = payload.llm_config.model_dump() if payload.llm_config else None
    return qa_service.ask(course_id, payload.question, payload.top_k, llm_config)


@router.get("/history", response_model=list[QAHistoryOut])
def get_qa_history(course_id: int, keyword: str = "", limit: int = 100, offset: int = 0):
    return qa_service.history(course_id, keyword=keyword, limit=limit, offset=offset)


@router.get("/history/{qa_id}", response_model=QAHistoryOut)
def get_qa_history_item(course_id: int, qa_id: int):
    return qa_service.get_history_item(course_id, qa_id)


@router.delete("/history/{qa_id}", response_model=DeleteResponse)
def delete_qa_history_item(course_id: int, qa_id: int):
    return qa_service.delete_history_item(course_id, qa_id)


@router.delete("/history", response_model=DeleteResponse)
def delete_qa_history_items(course_id: int, payload: BatchDeleteRequest):
    return qa_service.delete_history_items(course_id, payload.ids)
