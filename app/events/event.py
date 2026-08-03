from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class Event:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: uuid4().hex)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def type_name(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True, slots=True)
class PipelineDispatchStarted(Event):
    def __init__(self, *, session_id: str, update_type: str) -> None:
        super().__init__(
            name="pipeline.dispatch_started",
            payload={"session_id": session_id, "update_type": update_type},
        )


@dataclass(frozen=True, slots=True)
class PipelineDispatchCompleted(Event):
    def __init__(self, *, session_id: str, handled: bool, handler_name: str | None) -> None:
        super().__init__(
            name="pipeline.dispatch_completed",
            payload={
                "session_id": session_id,
                "handled": handled,
                "handler_name": handler_name,
            },
        )


@dataclass(frozen=True, slots=True)
class PipelineDispatchFailed(Event):
    def __init__(self, *, session_id: str, error: str) -> None:
        super().__init__(
            name="pipeline.dispatch_failed",
            payload={"session_id": session_id, "error": error},
        )
