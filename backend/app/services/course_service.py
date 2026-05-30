from fastapi import HTTPException

from modules import db


def ensure_course(course_id: int) -> dict:
    course = db.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在。")
    return course


def create_course(name: str, description: str = "") -> dict:
    if not name.strip():
        raise HTTPException(status_code=400, detail="课程名称不能为空。")
    try:
        course_id = db.create_course(name, description)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"创建课程失败：{exc}") from exc
    return ensure_course(course_id)


def list_courses() -> list[dict]:
    return db.list_courses()


def get_course(course_id: int) -> dict:
    return ensure_course(course_id)


def get_course_stats(course_id: int) -> dict:
    ensure_course(course_id)
    return {
        "course_id": course_id,
        "document_count": db.count_documents(course_id),
        "chunk_count": db.count_chunks(course_id),
        "qa_count": db.count_qa_history(course_id),
        "question_count": db.count_question_records(course_id),
    }
