from __future__ import annotations

from pydantic import BaseModel

from config import CHAT_MODEL, OPENAI_COMPATIBLE_BASE_URL


class AppSettings(BaseModel):
    app_name: str = "COURSE_RAG_SYSTEM"
    api_prefix: str = "/api"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5173",
    ]
    default_base_url: str = OPENAI_COMPATIBLE_BASE_URL
    default_chat_model: str = CHAT_MODEL


settings = AppSettings()
