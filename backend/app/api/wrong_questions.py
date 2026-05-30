from fastapi import APIRouter

from app.schemas.wrong_question import (
    WrongQuestionBatchDeleteRequest,
    WrongQuestionCreate,
    WrongQuestionDeleteResponse,
    WrongQuestionOut,
    WrongQuestionUpdate,
)
from app.services import wrong_question_service

router = APIRouter(prefix="/courses/{course_id}/wrong-questions", tags=["wrong-questions"])


@router.get("", response_model=list[WrongQuestionOut])
def list_wrong_questions(
    course_id: int,
    keyword: str = "",
    status: str = "",
    knowledge_point: str = "",
    limit: int = 100,
    offset: int = 0,
):
    return wrong_question_service.list_items(course_id, keyword, status, knowledge_point, limit, offset)


@router.post("", response_model=WrongQuestionOut)
def create_wrong_question(course_id: int, payload: WrongQuestionCreate):
    return wrong_question_service.create(course_id, payload.model_dump())


@router.get("/{wrong_id}", response_model=WrongQuestionOut)
def get_wrong_question(course_id: int, wrong_id: int):
    return wrong_question_service.get_item(course_id, wrong_id)


@router.patch("/{wrong_id}", response_model=WrongQuestionOut)
def update_wrong_question(course_id: int, wrong_id: int, payload: WrongQuestionUpdate):
    return wrong_question_service.update(course_id, wrong_id, payload.model_dump(exclude_unset=True))


@router.post("/{wrong_id}/review", response_model=WrongQuestionOut)
def mark_wrong_question_reviewed(course_id: int, wrong_id: int):
    return wrong_question_service.mark_reviewed(course_id, wrong_id)


@router.delete("/{wrong_id}", response_model=WrongQuestionDeleteResponse)
def delete_wrong_question(course_id: int, wrong_id: int):
    return wrong_question_service.delete_item(course_id, wrong_id)


@router.delete("", response_model=WrongQuestionDeleteResponse)
def delete_wrong_questions(course_id: int, payload: WrongQuestionBatchDeleteRequest):
    return wrong_question_service.delete_items(course_id, payload.ids)
