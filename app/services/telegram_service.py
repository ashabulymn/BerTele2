from __future__ import annotations

import logging
from dataclasses import dataclass

from fastapi import HTTPException, status
from telethon import TelegramClient
from telethon.sessions import StringSession

from app.core.config import Settings
from app.schemas.telegram import DialogInfo, SendMessageResponse, UserInfo


@dataclass
class TelegramService:
    settings: Settings
    logger: logging.Logger

    def __post_init__(self) -> None:
        if self.settings.telegram_api_id is None or self.settings.telegram_api_hash is None:
            self.client = None
            self.logger.warning("Telegram client is disabled because API credentials are missing")
            return
        session = StringSession(self.settings.telegram_session_string or "")
        self.client = TelegramClient(
            session,
            self.settings.telegram_api_id,
            self.settings.telegram_api_hash,
        )

    async def connect(self) -> None:
        if self.client is None:
            return
        self.logger.info("Connecting Telegram client")
        await self.client.connect()

    async def disconnect(self) -> None:
        if self.client is None:
            return
        self.logger.info("Disconnecting Telegram client")
        await self.client.disconnect()

    def _require_client(self) -> TelegramClient:
        if self.client is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram client is not configured",
            )
        return self.client

    async def get_me(self) -> UserInfo:
        client = self._require_client()
        me = await client.get_me()
        return UserInfo(
            id=me.id,
            username=getattr(me, "username", None),
            first_name=getattr(me, "first_name", None),
            last_name=getattr(me, "last_name", None),
            phone=getattr(me, "phone", None),
            is_bot=bool(getattr(me, "bot", False)),
        )

    async def send_message(self, peer: str, message: str) -> SendMessageResponse:
        client = self._require_client()
        sent = await client.send_message(peer, message)
        return SendMessageResponse(message_id=sent.id, peer=peer)

    async def list_dialogs(self) -> list[DialogInfo]:
        client = self._require_client()
        dialogs = await client.get_dialogs()
        result: list[DialogInfo] = []
        for dialog in dialogs:
            entity = dialog.entity
            result.append(
                DialogInfo(
                    id=dialog.id,
                    title=getattr(dialog, "title", None),
                    name=getattr(dialog, "name", None),
                    unread_count=getattr(dialog, "unread_count", None),
                    entity=entity.to_dict() if hasattr(entity, "to_dict") else {},
                )
            )
        return result
