from __future__ import annotations

import logging
from dataclasses import dataclass

from app.core.config import Settings
from app.telegram.manager import TelegramEngine


@dataclass
class TelegramService:
    settings: Settings
    logger: logging.Logger
    _engine: TelegramEngine | None = None

    @property
    def engine(self) -> TelegramEngine:
        if self._engine is None:
            self._engine = TelegramEngine(settings=self.settings, logger=self.logger)
        return self._engine

    async def connect(self) -> None:
        await self.engine.connect()

    async def disconnect(self) -> None:
        await self.engine.disconnect()

    async def get_me(self):
        return await self.engine.get_me()

    async def list_dialogs(self, limit: int = 50, offset: int = 0):
        return await self.engine.list_dialogs(limit=limit, offset=offset)

    async def get_dialog(self, dialog_id: int):
        return await self.engine.get_dialog(dialog_id)

    async def list_messages(self, dialog_id: int, limit: int = 50, offset: int = 0):
        return await self.engine.list_messages(dialog_id=dialog_id, limit=limit, offset=offset)

    async def send_message(self, peer: str, message: str):
        return await self.engine.send_message(peer, message)

    async def forward_messages(self, from_peer: str, to_peer: str, message_ids: list[int]):
        return await self.engine.forward_messages(from_peer, to_peer, message_ids)
