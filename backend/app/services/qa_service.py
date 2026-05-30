from __future__ import annotations

import json

from fastapi import HTTPException

from modules import db
from modules.rag_qa import ask_course
from app.services.course_service import ensure_course


def _parse_sources(value) -> list[dict]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return [{"source_file": value}]
    return []


def _normalize_item(item: dict) -> dict:
    normalized = dict(item)
    normalized["sources"] = _parse_sources(normalized.get("sources"))
    return normalized


def ask(course_id: int, question: str, top_k: int, llm_config: dict | None = None) -> dict:
    ensure_course(course_id)
    return ask_course(course_id, question, top_k, llm_config=llm_config)


def history(course_id: int, keyword: str = "", limit: int = 100, offset: int = 0) -> list[dict]:
    ensure_course(course_id)
    return [_normalize_item(item) for item in db.search_qa_history(course_id, keyword, limit, offset)]


def get_history_item(course_id: int, qa_id: int) -> dict:
    ensure_course(course_id)
    item = db.get_qa_history_item(course_id, qa_id)
    if not item:
        raise HTTPException(status_code=404, detail="问答历史不存在。")
    return _normalize_item(item)


def delete_history_item(course_id: int, qa_id: int) -> dict:
    ensure_course(course_id)
    deleted = db.delete_qa_history_item(course_id, qa_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="问答历史不存在或不属于当前课程。")
    return {"deleted": deleted}


def delete_history_items(course_id: int, ids: list[int]) -> dict:
    ensure_course(course_id)
    return {"deleted": db.delete_qa_history_items(course_id, ids)}
