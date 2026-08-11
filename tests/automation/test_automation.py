from __future__ import annotations

import logging

import pytest

from app.automation.actions import ActionRegistry, GoWASendMediaAction
from app.automation.engine import AutomationEngine
from app.automation.exceptions import ActionError, UnknownActionError, UnknownTriggerError
from app.automation.triggers import EventTrigger, TriggerRegistry
from app.events import EventBroker
from app.events.event import Event


@pytest.mark.anyio
async def test_event_trigger_matches_by_event_name() -> None:
    trigger = EventTrigger(name="on-dispatch", event_name="pipeline.dispatch_completed")
    event = Event(name="pipeline.dispatch_completed", payload={"session_id": "s-1"})

    assert trigger.matches(event) is True
    assert trigger.matches(Event(name="pipeline.dispatch_started")) is False


def test_trigger_registry_register_get_all() -> None:
    registry = TriggerRegistry()
    trigger = EventTrigger(name="on-dispatch", event_name="pipeline.dispatch_completed")
    registry.register(trigger)

    assert registry.get("on-dispatch") is trigger
    assert registry.all() == [trigger]


def test_trigger_registry_duplicate_raises() -> None:
    registry = TriggerRegistry()
    registry.register(EventTrigger(name="dup", event_name="a"))

    with pytest.raises(ValueError):
        registry.register(EventTrigger(name="dup", event_name="b"))


def test_trigger_registry_unknown_raises() -> None:
    registry = TriggerRegistry()

    with pytest.raises(UnknownTriggerError):
        registry.get("missing")


def test_trigger_registry_matching_filters() -> None:
    registry = TriggerRegistry()
    registry.register(EventTrigger(name="a", event_name="event.a"))
    registry.register(EventTrigger(name="b", event_name="event.b"))

    matches = registry.matching(Event(name="event.a"))

    assert [t.name for t in matches] == ["a"]


def test_action_registry_register_get_all() -> None:
    registry = ActionRegistry()
    action = GoWASendMediaAction(service=None)
    registry.register(action)

    assert registry.get("gowa.send_media") is action
    assert registry.all() == [action]


def test_action_registry_duplicate_raises() -> None:
    registry = ActionRegistry()
    registry.register(GoWASendMediaAction(service=None))

    with pytest.raises(ValueError):
        registry.register(GoWASendMediaAction(service=None))


def test_action_registry_unknown_raises() -> None:
    registry = ActionRegistry()

    with pytest.raises(UnknownActionError):
        registry.get("missing")


@pytest.mark.anyio
async def test_gowa_send_media_action_missing_payload_field() -> None:
    action = GoWASendMediaAction(service=None)
    payload = {
        "chat_id": "c-1",
        "storage_key": "key",
        "metadata": {"type": "photo", "mime_type": "image/png", "size": 10, "sha256": "abc"},
    }

    with pytest.raises(ActionError, match="device_id"):
        await action.execute(payload)


@pytest.mark.anyio
async def test_gowa_send_media_action_invalid_media_type() -> None:
    action = GoWASendMediaAction(service=None)
    payload = {
        "device_id": "d-1",
        "chat_id": "c-1",
        "storage_key": "key",
        "metadata": {"type": "unknown", "mime_type": "image/png", "size": 10, "sha256": "abc"},
    }

    with pytest.raises(ActionError, match="Unsupported media type"):
        await action.execute(payload)


@pytest.mark.anyio
async def test_engine_fires_trigger_and_runs_actions() -> None:
    broker = EventBroker(logger=logging.getLogger("test.automation"))
    engine = AutomationEngine(broker=broker)
    engine.triggers.register(EventTrigger(name="on-dispatch", event_name="pipeline.dispatch_completed"))

    executed: list[str] = []

    class FakeAction:
        name = "fake.action"

        async def execute(self, payload: dict) -> dict:
            executed.append(payload["session_id"])
            return {"ok": True}

    engine.actions.register(FakeAction())

    published: list[str] = []
    original_publish = broker.publish

    async def capture(event) -> None:
        published.append(event.name)
        await original_publish(event)

    broker.publish = capture  # type: ignore[method-assign]

    await engine._on_event(Event(name="pipeline.dispatch_completed", payload={"session_id": "s-1"}))

    assert executed == ["s-1"]
    assert "automation.triggered" in published
    assert "automation.action_started" in published
    assert "automation.action_completed" in published


@pytest.mark.anyio
async def test_engine_publishes_failed_event_on_action_error() -> None:
    broker = EventBroker(logger=logging.getLogger("test.automation"))
    engine = AutomationEngine(broker=broker)
    engine.triggers.register(EventTrigger(name="on-dispatch", event_name="pipeline.dispatch_completed"))

    class FailingAction:
        name = "failing.action"

        async def execute(self, payload: dict) -> dict:
            raise ActionError("boom")

    engine.actions.register(FailingAction())

    published: list[str] = []
    original_publish = broker.publish

    async def capture(event) -> None:
        published.append(event.name)
        await original_publish(event)

    broker.publish = capture  # type: ignore[method-assign]

    await engine._on_event(Event(name="pipeline.dispatch_completed", payload={"session_id": "s-1"}))

    assert "automation.action_failed" in published
    assert "automation.action_completed" not in published


@pytest.mark.anyio
async def test_engine_ignores_non_matching_events() -> None:
    broker = EventBroker(logger=logging.getLogger("test.automation"))
    engine = AutomationEngine(broker=broker)
    engine.triggers.register(EventTrigger(name="on-dispatch", event_name="pipeline.dispatch_completed"))

    executed: list[str] = []

    class FakeAction:
        name = "fake.action"

        async def execute(self, payload: dict) -> dict:
            executed.append("ran")
            return {}

    engine.actions.register(FakeAction())

    await engine._on_event(Event(name="pipeline.dispatch_started", payload={}))

    assert executed == []