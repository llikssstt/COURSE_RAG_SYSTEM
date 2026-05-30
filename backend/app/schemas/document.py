from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    course_id: int
    file_name: str
    file_type: str
    file_path: str
    upload_time: str
    parse_status: str


class UploadResult(BaseModel):
    file_name: str
    document_id: Optional[int] = None
    status: str
    error: Optional[str] = None
