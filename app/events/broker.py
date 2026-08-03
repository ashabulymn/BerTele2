from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.events.dispatcher import EventDispatcher
from app.events.event import Event
from app.events.publisher import EventPublisher
from app.events.queue import EventQueue
from app.events.registry import EventRegistry
from app.events.subscriber import EventHandler


@dataclass
class EventBroker:
    logger: logging.Logger
    registry: EventRegistry = field(default_factory=EventRegistry)
    queue: EventQueue = field(default_factory=EventQueue)

    def __post_init__(self) -> None:
        self.publisher = EventPublisher(queue=self.queue, logger=self.logger)
        self.dispatcher = EventDispatcher(registry=self.registry, queue=self.queue, logger=self.logger)

    async def publish(self, event: Event) -> None:
        await self.publisher.publish(event)

    def subscribe(self, event_type: type[Event], handler: EventHandler, *, name: str | None = None) -> None:
        self.registry.subscribe(event_type, handler, name=name)

    def start(self) -> None:
        self.dispatcher.start()

    async def stop(self) -> None:
        await self.dispatcher.stop()

