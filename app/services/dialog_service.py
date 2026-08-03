from __future__ import annotations

import logging
from dataclasses import dataclass

from app.services.chat_resolver import ChatResolver
from app.services.telegram_client_manager import TelegramClientManager
from app.telegram.dialogs import TelegramDialogService


@dataclass
class DialogService:
    client_manager: TelegramClientManager
    chat_resolver: ChatResolver
    logger: logging.Logger
    _service: TelegramDialogService | None = None

    def _engine(self) -> TelegramDialogService:
        if self._service is None:
            from app.telegram.entities import TelegramEntityResolver

            resolver = TelegramEntityResolver(client_pool=self.client_manager.pool)
            self._service = TelegramDialogService(client_pool=self.client_manager.pool, entity_resolver=resolver)
        return self._service

    async def list_dialogs(self, limit: int = 50, offset: int = 0):
        return await self._engine().list_dialogs(limit=limit, offset=offset)

    async def get_dialog(self, dialog_id: int):
        return await self._engine().get_dialog(dialog_id)
