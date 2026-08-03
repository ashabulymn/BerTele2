from __future__ import annotations

import logging
from dataclasses import dataclass

from fastapi import HTTPException, status
from telethon.tl.types import Channel, Chat, User

from app.services.telegram_client_manager import TelegramClientManager


@dataclass
class ChatResolver:
    client_manager: TelegramClientManager
    logger: logging.Logger

    async def resolve(self, peer: str | int):
        try:
            entity = await self.client_manager.call(
                lambda client: client.get_entity(peer),
                action=f"resolve {peer}",
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dialog not found") from exc

        if not isinstance(entity, (User, Chat, Channel)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported peer type")
        return entity
