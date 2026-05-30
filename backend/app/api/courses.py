from fastapi import APIRouter

from app.schemas.course import CourseCreate, CourseOut, CourseStats
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseOut])
def list_courses():
    return course_service.list_courses()


@router.post("", response_model=CourseOut)
def create_course(payload: CourseCreate):
    return course_service.create_course(payload.name, payload.description)


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int):
    return course_service.get_course(course_id)


@router.get("/{course_id}/stats", response_model=CourseStats)
def get_course_stats(course_id: int):
    return course_service.get_course_stats(course_id)
