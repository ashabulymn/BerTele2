from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from app.events.event import Event
from app.events.exceptions import EventRegistryError
from app.events.subscriber import EventHandler, Subscription


@dataclass
class EventRegistry:
    _subscriptions: dict[type[Event], list[Subscription]] = field(default_factory=lambda: defaultdict(list))

    def subscribe(self, event_type: type[Event], handler: EventHandler, *, name: str | None = None) -> None:
        self._subscriptions[event_type].append(Subscription(event_type=event_type, handler=handler, name=name))

    def handlers_for(self, event: Event) -> list[Subscription]:
        subscriptions: list[Subscription] = []
        for event_type, registered in self._subscriptions.items():
            if isinstance(event, event_type):
                subscriptions.extend(registered)
        if not subscriptions:
            return []
        return subscriptions

    def require_handlers(self, event: Event) -> list[Subscription]:
        handlers = self.handlers_for(event)
        if not handlers:
            raise EventRegistryError(f"No handlers registered for event type {event.type_name}")
        return handlers
