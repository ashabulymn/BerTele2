from __future__ import annotations

from fastapi import Request

from app.services.telegram_service import TelegramService


def get_telegram_service(request: Request) -> TelegramService:
    return request.app.state.container.telegram_service
