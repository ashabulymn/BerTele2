from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from telethon import events

from app.telegram.client import TelegramClientPool


@dataclass
class TelegramEventDispatcher:
    client_pool: TelegramClientPool
    logger: logging.Logger
    _handlers: list[tuple[object, Callable[..., Awaitable[None] | None]]] = field(default_factory=list)

    def on_new_message(self, handler):
        self._handlers.append((events.NewMessage, handler))
        return handler

    async def attach(self) -> None:
        for session_id in self.client_pool.registry._sessions:
            client = self.client_pool.client(session_id)
            for event_factory, handler in self._handlers:
                client.add_event_handler(handler, event_factory)
            self.logger.info("Attached %s Telegram event handlers to %s", len(self._handlers), session_id)
