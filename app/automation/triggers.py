"""Triggers for the Automation Engine (Epic A2).

A trigger detects a domain event and decides whether the bound actions
should run. Triggers are intentionally decoupled from the event broker:
the engine feeds each incoming event to every registered trigger.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol

from app.automation.exceptions import UnknownTriggerError
from app.events.event import Event

logger = logging.getLogger("app.automation.triggers")


class Trigger(Protocol):
    """Interface implemented by automation triggers."""

    name: str

    def matches(self, event: Event) -> bool:
        """Return True when the event should fire this trigger."""
        ...


@dataclass(frozen=True, slots=True)
class EventTrigger:
    """Fires when an event with a matching name is observed.

    Args:
        name: Unique trigger name used for registration and reporting.
        event_name: The event ``name`` (e.g. ``pipeline.dispatch_completed``)
            that activates this trigger.
    """

    name: str
    event_name: str

    def matches(self, event: Event) -> bool:
        return event.name == self.event_name


@dataclass
class TriggerRegistry:
    """Registry of named triggers."""

    _triggers: dict[str, Trigger] = field(default_factory=dict)

    def register(self, trigger: Trigger) -> None:
        """Register a trigger by its name.

        Args:
            trigger: The trigger to register.

        Raises:
            ValueError: If a trigger with the same name is already registered.
        """
        if trigger.name in self._triggers:
            raise ValueError(f"Trigger '{trigger.name}' is already registered")
        self._triggers[trigger.name] = trigger
        logger.info("Registered automation trigger", extra={"trigger_name": trigger.name})

    def get(self, name: str) -> Trigger:
        """Return a registered trigger by name.

        Raises:
            UnknownTriggerError: If no trigger with that name is registered.
        """
        try:
            return self._triggers[name]
        except KeyError as exc:
            raise UnknownTriggerError(f"Unknown trigger '{name}'") from exc

    def all(self) -> list[Trigger]:
        """Return all registered triggers."""
        return list(self._triggers.values())

    def matching(self, event: Event) -> list[Trigger]:
        """Return the triggers that match the given event."""
        return [trigger for trigger in self._triggers.values() if trigger.matches(event)]