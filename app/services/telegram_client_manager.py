from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TypeVar

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession

from app.core.config import Settings

T = TypeVar("T")


@dataclass
class TelegramClientManager:
    settings: Settings
    logger: logging.Logger
    _client: TelegramClient | None = field(init=False, default=None)
    _lock: asyncio.Lock = field(init=False, default_factory=asyncio.Lock)

    def __post_init__(self) -> None:
        if self.settings.telegram_api_id is None or self.settings.telegram_api_hash is None:
            self.logger.warning("Telegram client is disabled because API credentials are missing")
            return
        session = StringSession(self.settings.telegram_session_string or "")
        self._client = TelegramClient(
            session,
            self.settings.telegram_api_id,
            self.settings.telegram_api_hash,
        )

    @property
    def client(self) -> TelegramClient:
        if self._client is None:
            raise RuntimeError("Telegram client is not configured")
        return self._client

    def is_configured(self) -> bool:
        return self._client is not None

    async def connect(self) -> None:
        if self._client is None:
            return
        async with self._lock:
            if not self._client.is_connected():
                self.logger.info("Connecting Telegram client")
                await self._client.connect()

    async def disconnect(self) -> None:
        if self._client is None:
            return
        async with self._lock:
            if self._client.is_connected():
                self.logger.info("Disconnecting Telegram client")
                await self._client.disconnect()

    async def call(self, operation: Callable[[TelegramClient], Awaitable[T]], *, action: str) -> T:
        client = self.client
        while True:
            try:
                return await operation(client)
            except FloodWaitError as exc:
                wait_seconds = int(getattr(exc, "seconds", 1))
                self.logger.warning(
                    "Flood wait encountered during %s, retrying in %s seconds",
                    action,
                    wait_seconds,
                )
                await asyncio.sleep(wait_seconds)
            except Exception:
                self.logger.exception("Telegram operation failed during %s", action)
                raise
