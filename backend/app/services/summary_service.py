from __future__ import annotations

from modules.review_summary import generate_summary
from modules.rag_qa import format_sources
from app.services.course_service import ensure_course


def generate(course_id: int, summary_type: str, scope: str, top_k: int, llm_config: dict | None = None) -> dict:
    ensure_course(course_id)
    result = generate_summary(course_id, summary_type, scope, top_k, llm_config=llm_config)
    return {
        "summary": result["summary"],
        "sources": format_sources(result.get("contexts", [])),
    }
