from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import get_telegram_service
from app.schemas.telegram import DialogInfo, UserInfo
from app.services.telegram_service import TelegramService

router = APIRouter()


@router.get("/me", response_model=UserInfo)
async def me(service: TelegramService = Depends(get_telegram_service)) -> UserInfo:
    return await service.get_me()


@router.get("/dialogs", response_model=list[DialogInfo])
async def dialogs(service: TelegramService = Depends(get_telegram_service)) -> list[DialogInfo]:
    return await service.list_dialogs()

