from __future__ import annotations

from modules import db
from modules.rag_qa import ask_course
from app.services.course_service import ensure_course


def ask(course_id: int, question: str, top_k: int, llm_config: dict | None = None) -> dict:
    ensure_course(course_id)
    return ask_course(course_id, question, top_k, llm_config=llm_config)


def history(course_id: int) -> list[dict]:
    ensure_course(course_id)
    return db.list_qa_history(course_id, limit=100)
