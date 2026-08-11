from __future__ import annotations

import logging
from unittest.mock import AsyncMock

import pytest

from app.automation.actions import ActionRegistry, GoWASendMediaAction
from app.automation.engine import AutomationEngine
from app.automation.exceptions import ActionError, UnknownActionError, UnknownTriggerError
from app.automation.triggers import EventTrigger, TriggerRegistry
from app.events import EventBroker
from app.events.event import Event
from app.gowa.media.exceptions import GoWAMediaError
from app.gowa.media.service import GoWAMediaService
from app.media.models import MediaType
from app.media.pipeline.interfaces import MediaResource


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
async def test_gowa_send_media_action_delegates_to_service() -> None:
    """GoWASendMediaAction must actually delegate to GoWAMediaService.

    Verifies the action builds the MediaResource from the payload and
    forwards it together with device_id and chat_id to send_media(),
    then returns the service result.
    """
    service = AsyncMock(spec=GoWAMediaService)
    expected_result = {"status": "sent", "message_id": "m-1"}
    service.send_media.return_value = expected_result

    action = GoWASendMediaAction(service=service)  # type: ignore[arg-type]
    payload = {
        "device_id": "device-123",
        "chat_id": "chat-456",
        "storage_key": "media/storage/photo.png",
        "metadata": {
            "type": "photo",
            "mime_type": "image/png",
            "size": 2048,
            "sha256": "abc123",
            "filename": "photo.png",
            "caption": "A test photo",
        },
    }

    result = await action.execute(payload)

    service.send_media.assert_awaited_once()

    args = service.send_media.await_args.args
    assert len(args) == 3
    assert service.send_media.await_args.kwargs == {}

    resource, device_id, chat_id = args
    assert isinstance(resource, MediaResource)
    assert resource.storage_key == "media/storage/photo.png"
    assert resource.content is None
    assert resource.ready is True
    assert resource.metadata.type == MediaType.PHOTO
    assert resource.metadata.mime_type == "image/png"
    assert resource.metadata.size == 2048
    assert resource.metadata.sha256 == "abc123"
    assert resource.metadata.filename == "photo.png"
    assert resource.metadata.caption == "A test photo"

    assert device_id == "device-123"
    assert chat_id == "chat-456"

    assert result == expected_result


@pytest.mark.anyio
async def test_gowa_send_media_action_never_forwards_connection_credentials() -> None:
    """GoWA connection credentials are not action target parameters.

    The action's public API only accepts device_id, chat_id and the media
    payload; connection credentials (host, username, password, token,
    api_key, authorization) must never be forwarded to GoWAMediaService.
    """
    service = AsyncMock(spec=GoWAMediaService)
    service.send_media.return_value = {"status": "sent", "message_id": "m-42"}

    action = GoWASendMediaAction(service=service)  # type: ignore[arg-type]
    payload = {
        "device_id": "device-999",
        "chat_id": "chat-888",
        "storage_key": "media/storage/report.pdf",
        "metadata": {
            "type": "document",
            "mime_type": "application/pdf",
            "size": 5120,
            "sha256": "def456",
            "filename": "report.pdf",
        },
        "host": "https://gowa.example.internal",
        "username": "admin",
        "password": "s3cret",
        "token": "tok-123",
        "api_key": "key-456",
        "authorization": "Bearer very-secret-token",
    }

    result = await action.execute(payload)

    service.send_media.assert_awaited_once()

    args = service.send_media.await_args.args
    assert len(args) == 3
    assert service.send_media.await_args.kwargs == {}

    resource, device_id, chat_id = args
    assert device_id == "device-999"
    assert chat_id == "chat-888"

    assert isinstance(resource, MediaResource)
    assert resource.storage_key == "media/storage/report.pdf"
    assert resource.content is None
    assert resource.metadata.type == MediaType.DOCUMENT
    assert resource.metadata.mime_type == "application/pdf"
    assert resource.metadata.sha256 == "def456"

    # No credential value may reach the media service in any form.
    forwarded = repr(args)
    for secret in (
        "https://gowa.example.internal",
        "admin",
        "s3cret",
        "tok-123",
        "key-456",
        "Bearer very-secret-token",
    ):
        assert secret not in forwarded

    assert result == {"status": "sent", "message_id": "m-42"}


@pytest.mark.anyio
async def test_gowa_send_media_action_propagates_service_error() -> None:
    """A GoWAMediaError from the service is propagated per the contract."""
    service = AsyncMock(spec=GoWAMediaService)
    service.send_media.side_effect = GoWAMediaError("upstream failed")

    action = GoWASendMediaAction(service=service)  # type: ignore[arg-type]
    payload = {
        "device_id": "device-1",
        "chat_id": "chat-1",
        "storage_key": "key",
        "metadata": {"type": "photo", "mime_type": "image/png", "size": 10, "sha256": "abc"},
    }

    with pytest.raises(ActionError, match="upstream failed"):
        await action.execute(payload)

    service.send_media.assert_awaited_once()


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