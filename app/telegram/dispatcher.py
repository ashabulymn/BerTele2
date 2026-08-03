from __future__ import annotations

import logging
from dataclasses import dataclass, field

from telethon import events

from app.pipeline.message_pipeline import MessagePipeline
from app.telegram.client import TelegramClientPool


@dataclass
class TelegramEventDispatcher:
    client_pool: TelegramClientPool
    pipeline: MessagePipeline
    logger: logging.Logger
    _registered: bool = field(default=False, init=False)

    async def attach(self) -> None:
        if self._registered:
            return

        async def _handle(event):
            session_id = getattr(getattr(event, "client", None), "_session_id", "default")
            client = getattr(event, "client", None)
            await self.pipeline.dispatch(event, session_id=session_id, client=client)

        self.pipeline.register_handler(
            _handle,
            predicate=lambda context: bool(getattr(context.update, "message", None)),
            name="telegram.new_message",
        )

        for session_id in self.client_pool.registry._sessions:
            client = self.client_pool.client(session_id)
            client.add_event_handler(_handle, events.NewMessage)
            self.logger.info("Attached Telegram message pipeline to %s", session_id)

        self._registered = True
