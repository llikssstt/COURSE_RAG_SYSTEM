from modules import db
from modules.question_generator import generate_questions
from app.services.course_service import ensure_course


def generate(course_id: int, payload: dict) -> dict:
    ensure_course(course_id)
    return generate_questions(course_id=course_id, **payload)


def history(course_id: int) -> list[dict]:
    ensure_course(course_id)
    return db.list_question_records(course_id, limit=100)
