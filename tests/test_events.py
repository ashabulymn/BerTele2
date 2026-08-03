from __future__ import annotations

import logging

import pytest

from app.events import EventBroker, PipelineDispatchStarted
from app.pipeline.message_pipeline import MessagePipeline


@pytest.mark.anyio
async def test_event_broker_dispatches_typed_events() -> None:
    broker = EventBroker(logger=logging.getLogger("test.events"))
    received: list[str] = []

    async def handle(event: PipelineDispatchStarted) -> None:
        received.append(event.payload["session_id"])

    broker.subscribe(PipelineDispatchStarted, handle, name="test-handler")
    await broker.dispatcher.dispatch(
        PipelineDispatchStarted(session_id="session-1", update_type="message")
    )

    assert received == ["session-1"]


@pytest.mark.anyio
async def test_message_pipeline_publishes_events(monkeypatch: pytest.MonkeyPatch) -> None:
    broker = EventBroker(logger=logging.getLogger("test.pipeline"))
    published: list[str] = []

    async def capture(event) -> None:
        published.append(event.name)

    pipeline = MessagePipeline(logger=logging.getLogger("test.pipeline"), event_broker=broker)
    monkeypatch.setattr(broker, "publish", capture)

    async def handler(context) -> str:
        return str(context.update)

    pipeline.register_handler(handler, name="echo")
    result = await pipeline.dispatch("hello", session_id="s-1")

    assert result.handled is True
    assert "pipeline.dispatch_started" in published
