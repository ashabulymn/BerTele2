from __future__ import annotations


class EventBusError(RuntimeError):
    """Base error for internal event bus failures."""


class EventRegistryError(EventBusError):
    """Raised when event subscriptions or lookups fail."""


class EventQueueError(EventBusError):
    """Raised when queue operations fail."""

