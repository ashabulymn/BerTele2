from __future__ import annotations

from app.core.config import settings
from app.services.telegram_service import TelegramService


class AppContainer:
    def __init__(self) -> None:
        self.telegram_service = TelegramService(settings=settings)

    async def start(self) -> None:
        await self.telegram_service.connect()

    async def stop(self) -> None:
        await self.telegram_service.disconnect()

