from __future__ import annotations

import logging
from dataclasses import dataclass

from app.events.event import Event
from app.events.queue import EventQueue


@dataclass
class EventPublisher:
    queue: EventQueue
    logger: logging.Logger

    async def publish(self, event: Event) -> None:
        self.logger.info("Publishing event", extra={"event_name": event.name, "event_type": event.type_name})
        await self.queue.put(event)
