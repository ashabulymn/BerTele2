"""Domain events emitted by the Automation Engine (Epic A2)."""

from __future__ import annotations

from app.events.event import Event


class AutomationTriggered(Event):
    """Emitted when a trigger fires and its bound actions are about to run."""

    def __init__(self, *, trigger_name: str, event_name: str, payload: dict) -> None:
        super().__init__(
            name="automation.triggered",
            payload={
                "trigger_name": trigger_name,
                "event_name": event_name,
                "payload": payload,
            },
        )


class AutomationActionStarted(Event):
    """Emitted when an action begins executing."""

    def __init__(self, *, trigger_name: str, action_name: str, run_id: str) -> None:
        super().__init__(
            name="automation.action_started",
            payload={
                "trigger_name": trigger_name,
                "action_name": action_name,
                "run_id": run_id,
            },
        )


class AutomationActionCompleted(Event):
    """Emitted when an action finishes successfully."""

    def __init__(self, *, trigger_name: str, action_name: str, run_id: str, result: dict) -> None:
        super().__init__(
            name="automation.action_completed",
            payload={
                "trigger_name": trigger_name,
                "action_name": action_name,
                "run_id": run_id,
                "result": result,
            },
        )


class AutomationActionFailed(Event):
    """Emitted when an action raises an error."""

    def __init__(self, *, trigger_name: str, action_name: str, run_id: str, error: str) -> None:
        super().__init__(
            name="automation.action_failed",
            payload={
                "trigger_name": trigger_name,
                "action_name": action_name,
                "run_id": run_id,
                "error": error,
            },
        )