from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException

from app.services.course_service import ensure_course
from modules import db


def _parse_sources(value: Any) -> list[dict[str, Any]]:
    if not value:
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return [{"source_file": value}]
    return []


def _normalize(item: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(item)
    normalized["sources"] = _parse_sources(normalized.get("sources"))
    return normalized


def list_items(
    course_id: int,
    keyword: str = "",
    status: str = "",
    knowledge_point: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    ensure_course(course_id)
    return [
        _normalize(item)
        for item in db.list_wrong_questions(course_id, keyword, status, knowledge_point, limit, offset)
    ]


def create(course_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    ensure_course(course_id)
    if not payload.get("question_content", "").strip():
        raise HTTPException(status_code=400, detail="错题题干不能为空。")
    wrong_id = db.add_wrong_question(
        course_id=course_id,
        question_id=payload.get("question_id"),
        source_type=payload.get("source_type", "manual"),
        question_type=payload.get("question_type", ""),
        difficulty=payload.get("difficulty", ""),
        question_content=payload.get("question_content", ""),
        user_answer=payload.get("user_answer", ""),
        correct_answer=payload.get("correct_answer", ""),
        analysis=payload.get("analysis", ""),
        knowledge_point=payload.get("knowledge_point", ""),
        sources=payload.get("sources", []),
        note=payload.get("note", ""),
    )
    return get_item(course_id, wrong_id)


def get_item(course_id: int, wrong_id: int) -> dict[str, Any]:
    ensure_course(course_id)
    item = db.get_wrong_question(course_id, wrong_id)
    if not item:
        raise HTTPException(status_code=404, detail="错题不存在或不属于当前课程。")
    return _normalize(item)


def update(course_id: int, wrong_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    ensure_course(course_id)
    if payload.get("status") not in {None, "未掌握", "已掌握"}:
        raise HTTPException(status_code=400, detail="状态只能是未掌握或已掌握。")
    updated = db.update_wrong_question(
        course_id,
        wrong_id,
        note=payload.get("note"),
        status=payload.get("status"),
        user_answer=payload.get("user_answer"),
    )
    if updated == 0 and not db.get_wrong_question(course_id, wrong_id):
        raise HTTPException(status_code=404, detail="错题不存在或不属于当前课程。")
    return get_item(course_id, wrong_id)


def mark_reviewed(course_id: int, wrong_id: int) -> dict[str, Any]:
    ensure_course(course_id)
    updated = db.mark_wrong_question_reviewed(course_id, wrong_id)
    if updated == 0:
        raise HTTPException(status_code=404, detail="错题不存在或不属于当前课程。")
    return get_item(course_id, wrong_id)


def delete_item(course_id: int, wrong_id: int) -> dict[str, int]:
    ensure_course(course_id)
    deleted = db.delete_wrong_question(course_id, wrong_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="错题不存在或不属于当前课程。")
    return {"deleted": deleted}


def delete_items(course_id: int, ids: list[int]) -> dict[str, int]:
    ensure_course(course_id)
    return {"deleted": db.delete_wrong_questions(course_id, ids)}
