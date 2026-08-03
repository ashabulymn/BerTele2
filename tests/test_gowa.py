from __future__ import annotations

import asyncio
from types import TracebackType
from typing import Any, Self

import httpx
import pytest

from plugins.gowa.client import GoWAClient
from plugins.gowa.config import GoWAConfig
from plugins.gowa.mapper import map_outgoing_payload_to_event, map_webhook_to_event
from plugins.gowa.models import GoWAInboundEvent, GoWAOutboundEvent
from plugins.gowa.plugin import GoWAPlugin


def test_gowa_status_endpoint(client) -> None:
    response = client.get("/connectors/gowa/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["provider"] == "gowa"


def test_gowa_health_endpoint(client) -> None:
    response = client.get("/connectors/gowa/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["provider"] == "gowa"
    assert payload["healthy"] is True


def test_gowa_webhook_endpoint(client) -> None:
    response = client.post(
        "/connectors/gowa/webhook",
        json={
            "from": "15551234567",
            "to": "15557654321",
            "type": "text",
            "text": "hello from GoWA",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "accepted"
    assert payload["message_type"] == "text"


def test_gowa_send_endpoint(client) -> None:
    response = client.post(
        "/connectors/gowa/send",
        json={
            "to": "15557654321",
            "type": "image",
            "media_url": "https://example.com/image.jpg",
            "caption": "hello",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "queued"
    assert payload["provider"] == "gowa"
    assert payload["message_type"] == "image"


@pytest.mark.anyio
async def test_gowa_webhook_publishes_to_event_bus() -> None:
    connector = GoWAPlugin(config=GoWAConfig(use_mock_transport=True))
    received: list[str] = []

    async def handle(event: GoWAInboundEvent) -> None:
        received.append(event.payload["from_number"])

    connector.broker.subscribe(GoWAInboundEvent, handle, name="capture")
    event = map_webhook_to_event({"from": "15551234567", "to": "15557654321", "type": "text", "text": "hello"})
    await connector.broker.publish(event)
    await connector.broker.dispatcher.dispatch(event)

    assert received == ["15551234567"]


@pytest.mark.anyio
async def test_gowa_event_bus_to_transport() -> None:
    connector = GoWAPlugin(config=GoWAConfig(use_mock_transport=True))
    sent: list[dict[str, Any]] = []

    async def fake_send(payload: dict[str, Any]) -> dict[str, Any]:
        sent.append(payload)
        return {"status": "accepted", "provider": "gowa"}

    connector.client.send_message = fake_send  # type: ignore[assignment]

    event = GoWAOutboundEvent(
        recipient="15557654321",
        message_type="image",
        media_url="https://example.com/image.jpg",
        caption="hello",
    )
    await connector.broker.dispatcher.dispatch(event)

    assert sent and sent[0]["to"] == "15557654321"
    assert sent[0]["type"] == "image"


def test_gowa_mapper_round_trip() -> None:
    webhook = {"from": "15551234567", "to": "15557654321", "type": "image", "media_url": "https://example.com/pic.jpg"}
    event = map_webhook_to_event(webhook)
    assert event.payload["from_number"] == "15551234567"
    assert event.payload["message_type"] == "image"

    message = map_outgoing_payload_to_event({"to": "15557654321", "type": "reply", "reply_to": "abc123", "text": "hi"})
    assert message.payload["recipient"] == "15557654321"
    assert message.payload["message_type"] == "reply"


def test_gowa_client_retries_exponential_backoff(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    class FakeResponse:
        status_code = 200

        @property
        def content(self) -> bytes:
            return b'{"status": "ok"}'

        def json(self) -> dict[str, Any]:
            return {"status": "ok"}

        def raise_for_status(self) -> None:
            return None

    class FakeClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> None:
            return None

        async def post(self, url: str, json: dict[str, Any], headers: dict[str, str]) -> FakeResponse:
            calls.append(1)
            if len(calls) < 3:
                raise httpx.HTTPError("temporary failure")
            return FakeResponse()

    async def fake_sleep(delay: float) -> None:
        return None

    monkeypatch.setattr("plugins.gowa.client.httpx.AsyncClient", FakeClient)
    monkeypatch.setattr("plugins.gowa.client.asyncio.sleep", fake_sleep)

    client = GoWAClient(config=GoWAConfig(use_mock_transport=False, max_retries=3, base_url="http://localhost:8080"))
    result = asyncio.run(client.send_message({"to": "123", "type": "text", "text": "hi"}))

    assert result["status"] == "ok"
    assert len(calls) == 3
