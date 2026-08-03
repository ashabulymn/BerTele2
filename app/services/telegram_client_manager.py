from __future__ import annotations

import logging
from dataclasses import dataclass

from app.core.config import Settings
from app.telegram.client import TelegramClientPool


@dataclass
class TelegramClientManager:
    settings: Settings
    logger: logging.Logger
    _pool: TelegramClientPool | None = None

    @property
    def pool(self) -> TelegramClientPool:
        if self._pool is None:
            from app.telegram.manager import TelegramEngine

            self._pool = TelegramEngine(settings=self.settings, logger=self.logger).client_pool
        return self._pool

    def is_configured(self) -> bool:
        return self.pool.configured()

    async def connect(self) -> None:
        await self.pool.connect()

    async def disconnect(self) -> None:
        await self.pool.disconnect()

    async def call(self, operation, *, action: str):
        return await self.pool.call(operation, action=action)
