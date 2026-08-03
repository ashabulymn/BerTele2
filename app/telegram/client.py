from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession

from app.telegram.exceptions import TelegramEngineError, TelegramNotConfiguredError
from app.telegram.reconnect import TelegramReconnectPolicy
from app.telegram.session import TelegramSession, TelegramSessionRegistry


@dataclass
class TelegramClientPool:
    registry: TelegramSessionRegistry
    logger: logging.Logger
    reconnect_policy: TelegramReconnectPolicy = field(default_factory=TelegramReconnectPolicy)
    _clients: dict[str, TelegramClient] = field(default_factory=dict, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    def _build_client(self, session: TelegramSession) -> TelegramClient:
        return TelegramClient(
            StringSession(session.session_string or ""),
            session.api_id,
            session.api_hash,
        )

    async def connect(self) -> None:
        if not self.registry.configured():
            self.logger.warning("Telegram engine disabled: no configured sessions")
            return
        async with self._lock:
            for session in self.registry.all():
                client = self._clients.get(session.session_id) or self._build_client(session)
                self._clients[session.session_id] = client
                if not client.is_connected():
                    self.logger.info("Connecting Telegram session %s", session.session_id)
                    await client.connect()

    async def disconnect(self) -> None:
        async with self._lock:
            for session_id, client in list(self._clients.items()):
                if client.is_connected():
                    self.logger.info("Disconnecting Telegram session %s", session_id)
                    await client.disconnect()
            self._clients.clear()

    def configured(self) -> bool:
        return self.registry.configured()

    def client(self, session_id: str = "default") -> TelegramClient:
        try:
            return self._clients[session_id]
        except KeyError as exc:
            raise TelegramNotConfiguredError("Telegram client is not configured") from exc

    async def call(self, operation, *, action: str, session_id: str = "default"):
        client = self.client(session_id)
        attempt = 1
        while True:
            try:
                if not client.is_connected():
                    await self._reconnect(client, session_id=session_id)
                return await operation(client)
            except FloodWaitError as exc:
                wait_seconds = int(getattr(exc, "seconds", 1))
                self.logger.warning("Flood wait during %s, sleeping %s seconds", action, wait_seconds)
                await asyncio.sleep(wait_seconds)
            except TelegramEngineError:
                raise
            except Exception:
                if attempt >= self.reconnect_policy.max_attempts:
                    self.logger.exception("Telegram operation failed during %s", action)
                    raise
                delay = self.reconnect_policy.delay_for(attempt)
                self.logger.warning(
                    "Telegram operation failed during %s, reconnecting in %.1f seconds",
                    action,
                    delay,
                )
                await asyncio.sleep(delay)
                await self._reconnect(client, session_id=session_id)
                attempt += 1

    async def _reconnect(self, client: TelegramClient, *, session_id: str) -> None:
        async with self._lock:
            if not client.is_connected():
                self.logger.info("Reconnecting Telegram session %s", session_id)
                await client.connect()
