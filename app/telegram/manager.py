from __future__ import annotations

import logging
from dataclasses import dataclass

from fastapi import HTTPException, status

from app.core.config import Settings
from app.schemas.dialogs import (
    DialogInfo,
    ListDialogsResponse,
    ListMessagesResponse,
    SendMessageResponse,
)
from app.schemas.telegram import UserInfo
from app.telegram.client import TelegramClientPool
from app.telegram.dialogs import TelegramDialogService
from app.telegram.entities import TelegramEntityResolver
from app.telegram.messages import TelegramMessageService
from app.telegram.session import TelegramSessionRegistry


@dataclass
class TelegramEngine:
    settings: Settings
    logger: logging.Logger

    def __post_init__(self) -> None:
        self.session_registry = TelegramSessionRegistry(settings=self.settings)
        self.client_pool = TelegramClientPool(registry=self.session_registry, logger=self.logger)
        self.entity_resolver = TelegramEntityResolver(client_pool=self.client_pool)
        self.dialogs = TelegramDialogService(client_pool=self.client_pool, entity_resolver=self.entity_resolver)
        self.messages = TelegramMessageService(client_pool=self.client_pool, entity_resolver=self.entity_resolver)

    async def connect(self) -> None:
        await self.client_pool.connect()

    async def disconnect(self) -> None:
        await self.client_pool.disconnect()

    def _require_client(self) -> None:
        if not self.client_pool.configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram client is not configured",
            )

    async def get_me(self) -> UserInfo:
        self._require_client()
        me = await self.client_pool.call(lambda client: client.get_me(), action="get me")
        return UserInfo(
            id=me.id,
            username=getattr(me, "username", None),
            first_name=getattr(me, "first_name", None),
            last_name=getattr(me, "last_name", None),
            phone=getattr(me, "phone", None),
            is_bot=bool(getattr(me, "bot", False)),
        )

    async def list_dialogs(self, limit: int = 50, offset: int = 0) -> ListDialogsResponse:
        self._require_client()
        return await self.dialogs.list_dialogs(limit=limit, offset=offset)

    async def get_dialog(self, dialog_id: int) -> DialogInfo:
        self._require_client()
        return await self.dialogs.get_dialog(dialog_id)

    async def list_messages(self, dialog_id: int, limit: int = 50, offset: int = 0) -> ListMessagesResponse:
        self._require_client()
        return await self.messages.list_messages(dialog_id=dialog_id, limit=limit, offset=offset)

    async def send_message(self, peer: str, message: str) -> SendMessageResponse:
        self._require_client()
        return await self.messages.send_message(peer, message)

    async def forward_messages(self, from_peer: str, to_peer: str, message_ids: list[int]):
        self._require_client()
        return await self.messages.forward_messages(from_peer, to_peer, message_ids)
