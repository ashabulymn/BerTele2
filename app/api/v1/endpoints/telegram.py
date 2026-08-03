from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_telegram_service
from app.schemas.telegram import UserInfo
from app.services.telegram_service import TelegramService

router = APIRouter()


@router.get("/me", response_model=UserInfo)
async def me(service: Annotated[TelegramService, Depends(get_telegram_service)]) -> UserInfo:
    return await service.get_me()
