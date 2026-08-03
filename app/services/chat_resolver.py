from __future__ import annotations

import logging
from dataclasses import dataclass

from app.services.telegram_client_manager import TelegramClientManager
from app.telegram.entities import TelegramEntityResolver


@dataclass
class ChatResolver:
    client_manager: TelegramClientManager
    logger: logging.Logger
    _resolver: TelegramEntityResolver | None = None

    async def resolve(self, peer: str | int):
        if self._resolver is None:
            self._resolver = TelegramEntityResolver(client_pool=self.client_manager.pool)
        return await self._resolver.resolve(peer)
