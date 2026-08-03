from __future__ import annotations

from typing import Any

import pytest

from plugins.n8n.config import N8NConfig
from plugins.n8n.mapper import map_send_payload_to_event, map_webhook_to_event
from plugins.n8n.models import N8NInboundEvent, N8NOutboundEvent
from plugins.n8n.plugin import N8NPlugin


def test_n8n_status_endpoint(client) -> None:
    response = client.get("/connectors/n8n/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["provider"] == "n8n"


def test_n8n_health_endpoint(client) -> None:
    response = client.get("/connectors/n8n/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["provider"] == "n8n"
    assert payload["healthy"] is True


def test_n8n_event_endpoint(client) -> None:
    response = client.post(
        "/connectors/n8n/events",
        json={
            "workflowId": "workflow-123",
            "executionId": "exec-456",
            "event": "message.received",
            "body": {"message": "hello from n8n"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "accepted"
    assert payload["provider"] == "n8n"
    assert payload["workflow_id"] == "workflow-123"


def test_n8n_send_endpoint(client) -> None:
    response = client.post(
        "/connectors/n8n/send",
        json={
            "workflowId": "workflow-789",
            "node": "main",
            "payload": {"message": "hello to n8n"},
            "metadata": {"source": "bertele2"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "queued"
    assert payload["provider"] == "n8n"
    assert payload["workflow_id"] == "workflow-789"


@pytest.mark.anyio
async def test_n8n_webhook_publishes_to_event_bus() -> None:
    connector = N8NPlugin(config=N8NConfig(use_mock_transport=True))
    received: list[str] = []

    async def handle(event: N8NInboundEvent) -> None:
        received.append(event.payload["workflow_id"])

    connector.broker.subscribe(N8NInboundEvent, handle, name="capture")
    event = map_webhook_to_event({"workflowId": "workflow-1", "event": "message.received", "body": {"message": "hello"}})
    await connector.broker.publish(event)
    await connector.broker.dispatcher.dispatch(event)

    assert received == ["workflow-1"]


@pytest.mark.anyio
async def test_n8n_event_bus_to_transport() -> None:
    connector = N8NPlugin(config=N8NConfig(use_mock_transport=True))
    sent: list[dict[str, Any]] = []

    async def fake_send(payload: dict[str, Any]) -> dict[str, Any]:
        sent.append(payload)
        return {"status": "accepted", "provider": "n8n"}

    connector._send_to_n8n = fake_send  # type: ignore[assignment]

    event = N8NOutboundEvent(
        workflow_id="workflow-2",
        node="send",
        event_name="message.sent",
        payload={"message": "hello"},
        metadata={"source": "bertele2"},
    )
    await connector.broker.dispatcher.dispatch(event)

    assert sent and sent[0]["workflow_id"] == "workflow-2"
    assert sent[0]["event_name"] == "message.sent"


def test_n8n_mapper_round_trip() -> None:
    webhook = {"workflowId": "wf-1", "event": "message.received", "body": {"message": "hi"}}
    event = map_webhook_to_event(webhook)
    assert event.payload["workflow_id"] == "wf-1"
    assert event.payload["event"] == "message.received"

    send_request = map_send_payload_to_event({"workflow_id": "wf-2", "payload": {"message": "hello"}, "node": "send"})
    assert send_request.payload["message"] == "hello"
    assert send_request.payload["workflow_id"] == "wf-2"


def test_n8n_authentication_header() -> None:
    from plugins.n8n.webhook import _validate_credentials

    _validate_credentials("demo-key", None)
    _validate_credentials(None, "Bearer demo-token")
