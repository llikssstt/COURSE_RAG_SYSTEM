from __future__ import annotations

from pathlib import Path
import shutil

from fastapi import HTTPException, UploadFile

from config import UPLOAD_DIR
from modules import db
from app.services.course_service import ensure_course

ALLOWED_TYPES = {".pdf", ".docx", ".pptx"}


def list_documents(course_id: int) -> list[dict]:
    ensure_course(course_id)
    return db.list_documents(course_id)


def save_uploaded_files(course_id: int, files: list[UploadFile]) -> list[dict]:
    ensure_course(course_id)
    if not files:
        raise HTTPException(status_code=400, detail="请至少上传一个文件。")

    course_dir = UPLOAD_DIR / f"course_{course_id}"
    course_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for file in files:
        original_name = Path(file.filename or "").name
        suffix = Path(original_name).suffix.lower()
        if suffix not in ALLOWED_TYPES:
            results.append({"file_name": original_name, "status": "failed", "error": "仅支持 PDF、DOCX、PPTX。"})
            continue
        target = course_dir / original_name
        try:
            with target.open("wb") as out:
                shutil.copyfileobj(file.file, out)
            document_id = db.add_document(course_id, original_name, suffix, target)
            results.append({"file_name": original_name, "document_id": document_id, "status": "uploaded"})
        except Exception as exc:
            results.append({"file_name": original_name, "status": "failed", "error": str(exc)})
        finally:
            file.file.close()
    return results
