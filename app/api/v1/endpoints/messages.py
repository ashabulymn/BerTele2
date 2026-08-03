from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_telegram_service
from app.schemas.telegram import SendMessageRequest, SendMessageResponse
from app.services.telegram_service import TelegramService

router = APIRouter()


@router.post("/messages/send", response_model=SendMessageResponse, status_code=status.HTTP_200_OK)
async def send_message(
    payload: SendMessageRequest,
    service: Annotated[TelegramService, Depends(get_telegram_service)],
) -> SendMessageResponse:
    return await service.send_message(payload.peer, payload.message)
