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
from app.services.chat_resolver import ChatResolver
from app.services.dialog_service import DialogService
from app.services.message_service import MessageService
from app.services.telegram_client_manager import TelegramClientManager


@dataclass
class TelegramService:
    settings: Settings
    logger: logging.Logger

    def __post_init__(self) -> None:
        self.client_manager = TelegramClientManager(settings=self.settings, logger=self.logger)
        self.chat_resolver = ChatResolver(client_manager=self.client_manager, logger=self.logger)
        self.dialog_service = DialogService(
            client_manager=self.client_manager,
            chat_resolver=self.chat_resolver,
            logger=self.logger,
        )
        self.message_service = MessageService(
            client_manager=self.client_manager,
            chat_resolver=self.chat_resolver,
            logger=self.logger,
        )

    async def connect(self) -> None:
        await self.client_manager.connect()

    async def disconnect(self) -> None:
        await self.client_manager.disconnect()

    def _require_client(self) -> None:
        if not self.client_manager.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram client is not configured",
            )

    async def get_me(self) -> UserInfo:
        self._require_client()
        me = await self.client_manager.call(lambda client: client.get_me(), action="get me")
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
        return await self.dialog_service.list_dialogs(limit=limit, offset=offset)

    async def get_dialog(self, dialog_id: int) -> DialogInfo:
        self._require_client()
        return await self.dialog_service.get_dialog(dialog_id)

    async def list_messages(self, dialog_id: int, limit: int = 50, offset: int = 0) -> ListMessagesResponse:
        self._require_client()
        return await self.message_service.list_messages(dialog_id=dialog_id, limit=limit, offset=offset)

    async def send_message(self, peer: str, message: str) -> SendMessageResponse:
        self._require_client()
        return await self.message_service.send_message(peer, message)

    async def forward_messages(self, from_peer: str, to_peer: str, message_ids: list[int]):
        self._require_client()
        return await self.message_service.forward_messages(from_peer, to_peer, message_ids)
