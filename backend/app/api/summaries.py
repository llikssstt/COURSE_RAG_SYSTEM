from fastapi import APIRouter

from app.schemas.summary import SummaryGenerateRequest, SummaryGenerateResponse
from app.services import summary_service

router = APIRouter(prefix="/courses/{course_id}/summaries", tags=["summaries"])


@router.post("/generate", response_model=SummaryGenerateResponse)
def generate_summary(course_id: int, payload: SummaryGenerateRequest):
    llm_config = payload.llm_config.model_dump() if payload.llm_config else None
    return summary_service.generate(course_id, payload.summary_type, payload.scope, payload.top_k, llm_config)
