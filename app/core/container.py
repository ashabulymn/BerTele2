from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.core.database import create_engine, create_session_factory
from app.services.telegram_service import TelegramService


class AppContainer:
    def __init__(self) -> None:
        settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self.engine: AsyncEngine = create_engine(settings)
        self.session_factory: async_sessionmaker[AsyncSession] = create_session_factory(self.engine)
        self.telegram_service = TelegramService(settings=settings, logger=self.logger)

    async def start(self) -> None:
        self.logger.info("Starting application container")
        await self.telegram_service.connect()

    async def stop(self) -> None:
        self.logger.info("Stopping application container")
        await self.telegram_service.disconnect()
        await self.engine.dispose()
