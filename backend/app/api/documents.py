from fastapi import APIRouter, File, UploadFile

from app.schemas.document import DocumentOut, UploadResult
from app.services import document_service

router = APIRouter(prefix="/courses/{course_id}/documents", tags=["documents"])


@router.post("/upload", response_model=list[UploadResult])
def upload_documents(course_id: int, files: list[UploadFile] = File(...)):
    return document_service.save_uploaded_files(course_id, files)


@router.get("", response_model=list[DocumentOut])
def list_documents(course_id: int):
    return document_service.list_documents(course_id)
