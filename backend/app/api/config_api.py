from fastapi import APIRouter

from app.core.settings import settings

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/defaults")
def get_config_defaults():
    return {
        "base_url": settings.default_base_url,
        "model": settings.default_chat_model,
    }
