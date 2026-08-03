from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_telegram_service
from app.schemas.dialogs import DialogInfo, ListDialogsResponse, ListMessagesResponse
from app.services.telegram_service import TelegramService

router = APIRouter()


@router.get("/dialogs", response_model=ListDialogsResponse)
async def dialogs(
    service: Annotated[TelegramService, Depends(get_telegram_service)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ListDialogsResponse:
    return await service.list_dialogs(limit=limit, offset=offset)


@router.get("/dialogs/{dialog_id}", response_model=DialogInfo)
async def dialog(
    dialog_id: int,
    service: Annotated[TelegramService, Depends(get_telegram_service)],
) -> DialogInfo:
    return await service.get_dialog(dialog_id)


@router.get("/dialogs/{dialog_id}/messages", response_model=ListMessagesResponse)
async def dialog_messages(
    dialog_id: int,
    service: Annotated[TelegramService, Depends(get_telegram_service)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ListMessagesResponse:
    return await service.list_messages(dialog_id=dialog_id, limit=limit, offset=offset)
