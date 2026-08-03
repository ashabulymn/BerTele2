from __future__ import annotations

import logging
from dataclasses import dataclass

from app.services.chat_resolver import ChatResolver
from app.services.telegram_client_manager import TelegramClientManager
from app.telegram.messages import TelegramMessageService


@dataclass
class MessageService:
    client_manager: TelegramClientManager
    chat_resolver: ChatResolver
    logger: logging.Logger
    _service: TelegramMessageService | None = None

    def _engine(self) -> TelegramMessageService:
        if self._service is None:
            from app.telegram.entities import TelegramEntityResolver

            resolver = TelegramEntityResolver(client_pool=self.client_manager.pool)
            self._service = TelegramMessageService(client_pool=self.client_manager.pool, entity_resolver=resolver)
        return self._service

    async def send_message(self, peer: str, message: str):
        return await self._engine().send_message(peer, message)

    async def forward_messages(self, from_peer: str, to_peer: str, message_ids: list[int]):
        return await self._engine().forward_messages(from_peer, to_peer, message_ids)

    async def list_messages(self, dialog_id: int, limit: int = 50, offset: int = 0):
        return await self._engine().list_messages(dialog_id=dialog_id, limit=limit, offset=offset)
