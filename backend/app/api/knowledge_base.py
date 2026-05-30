from fastapi import APIRouter

from app.services import knowledge_service

router = APIRouter(prefix="/courses/{course_id}/knowledge-base", tags=["knowledge-base"])


@router.post("/rebuild")
def rebuild_knowledge_base(course_id: int):
    return knowledge_service.rebuild_course_knowledge_base(course_id)
