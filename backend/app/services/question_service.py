from __future__ import annotations

import json

from fastapi import HTTPException

from modules import db
from modules.question_generator import generate_questions
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


def _normalize_record(item: dict) -> dict:
    normalized = dict(item)
    normalized["sources"] = _parse_sources(normalized.get("sources"))
    return normalized


def generate(course_id: int, payload: dict) -> dict:
    ensure_course(course_id)
    return generate_questions(course_id=course_id, **payload)


def history(
    course_id: int,
    keyword: str = "",
    question_type: str = "",
    difficulty: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    ensure_course(course_id)
    return [
        _normalize_record(item)
        for item in db.search_question_records(course_id, keyword, question_type, difficulty, limit, offset)
    ]


def get_record(course_id: int, question_id: int) -> dict:
    ensure_course(course_id)
    item = db.get_question_record(course_id, question_id)
    if not item:
        raise HTTPException(status_code=404, detail="历史题目不存在。")
    return _normalize_record(item)


def delete_record(course_id: int, question_id: int) -> dict:
    ensure_course(course_id)
    deleted = db.delete_question_record(course_id, question_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="历史题目不存在或不属于当前课程。")
    return {"deleted": deleted}


def delete_records(course_id: int, ids: list[int]) -> dict:
    ensure_course(course_id)
    return {"deleted": db.delete_question_records(course_id, ids)}
