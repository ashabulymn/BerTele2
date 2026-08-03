from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.events.event import Event


class EventHandler(Protocol):
    async def __call__(self, event: Event) -> object: ...


@dataclass(frozen=True, slots=True)
class Subscription:
    event_type: type[Event]
    handler: EventHandler
    name: str | None = None


class EventSubscriber(Protocol):
    def subscribe(self, event_type: type[Event], handler: EventHandler, *, name: str | None = None) -> None: ...
