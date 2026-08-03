from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from app.events.event import Event
from app.events.exceptions import EventQueueError


@dataclass
class EventQueue:
    _queue: asyncio.Queue[Event] = field(default_factory=asyncio.Queue)

    async def put(self, event: Event) -> None:
        try:
            await self._queue.put(event)
        except Exception as exc:  # pragma: no cover - defensive
            raise EventQueueError("Failed to enqueue event") from exc

    async def get(self) -> Event:
        try:
            return await self._queue.get()
        except Exception as exc:  # pragma: no cover - defensive
            raise EventQueueError("Failed to dequeue event") from exc

    def empty(self) -> bool:
        return self._queue.empty()

