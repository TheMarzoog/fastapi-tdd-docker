from fastapi import APIRouter, Depends

from app.config import Settings, get_settings

router = APIRouter()


@router.get("/ping")
async def pong(setting: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": setting.environment,
        "testing": setting.testing,
    }
