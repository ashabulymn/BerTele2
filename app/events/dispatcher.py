from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field

from app.events.event import Event
from app.events.queue import EventQueue
from app.events.registry import EventRegistry


@dataclass
class EventDispatcher:
    registry: EventRegistry
    queue: EventQueue
    logger: logging.Logger
    _task: asyncio.Task[None] | None = field(default=None, init=False, repr=False)
    _stopped: asyncio.Event = field(default_factory=asyncio.Event, init=False, repr=False)

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._stopped.clear()
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._stopped.set()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def dispatch(self, event: Event) -> None:
        subscriptions = self.registry.handlers_for(event)
        if not subscriptions:
            self.logger.debug("No subscribers matched event", extra={"event_name": event.name})
            return
        for subscription in subscriptions:
            try:
                await subscription.handler(event)
            except Exception:
                self.logger.exception(
                    "Event subscriber failed",
                    extra={"event_name": event.name, "subscriber": subscription.name},
                )

    async def _run(self) -> None:
        while not self._stopped.is_set():
            event = await self.queue.get()
            await self.dispatch(event)

