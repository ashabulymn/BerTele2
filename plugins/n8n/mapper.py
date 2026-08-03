from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.events.event import Event

from .models import N8NInboundEvent, N8NOutboundEvent


def _payload_dict(value: Mapping[str, Any] | Event | None) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Event):
        return dict(value.payload)
    return dict(value)


def map_webhook_to_event(payload: Mapping[str, Any]) -> N8NInboundEvent:
    raw = dict(payload)
    body = raw.get("payload") if isinstance(raw.get("payload"), dict) else raw.get("body") or {}
    metadata = raw.get("metadata") or {}
    if isinstance(metadata, Mapping):
        metadata = dict(metadata)
    event_name = raw.get("event") or raw.get("event_name") or raw.get("type")
    normalized_payload = dict(body) if isinstance(body, Mapping) else {"value": body}
    for name in (
        "workflow_id",
        "workflowId",
        "execution_id",
        "executionId",
        "mode",
        "trigger",
        "event",
        "event_name",
        "metadata",
    ):
        if name in raw and name not in normalized_payload:
            normalized_payload[name] = raw[name]
    return N8NInboundEvent(
        workflow_id=raw.get("workflow_id") or raw.get("workflowId"),
        execution_id=raw.get("execution_id") or raw.get("executionId"),
        mode=raw.get("mode"),
        trigger=raw.get("trigger"),
        event=str(event_name) if event_name is not None else None,
        payload=normalized_payload,
        metadata=metadata,
    )


def map_send_payload_to_event(payload: Mapping[str, Any]) -> N8NOutboundEvent:
    raw = dict(payload)
    message_payload = raw.get("payload") if isinstance(raw.get("payload"), dict) else raw.get("body") or {}
    headers = raw.get("headers") or {}
    normalized_payload = dict(message_payload) if isinstance(message_payload, Mapping) else {"value": message_payload}
    for name in ("workflow_id", "workflowId", "node", "event_name", "eventName", "event"):
        if name in raw and name not in normalized_payload:
            normalized_payload[name] = raw[name]
    return N8NOutboundEvent(
        workflow_id=raw.get("workflow_id") or raw.get("workflowId"),
        node=raw.get("node"),
        event_name=raw.get("event_name") or raw.get("eventName") or raw.get("event"),
        payload=normalized_payload,
        headers=dict(headers) if isinstance(headers, Mapping) else {},
        metadata=dict(raw.get("metadata") or {}),
    )


def map_event_to_payload(event: Event | Mapping[str, Any]) -> dict[str, Any]:
    raw = _payload_dict(event)
    workflow_id = raw.get("workflow_id") or raw.get("workflowId")
    payload = raw.get("payload") if isinstance(raw.get("payload"), dict) else {
        key: value for key, value in raw.items() if key not in {"workflow_id", "workflowId", "node", "event_name", "eventName", "event", "headers", "metadata", "execution_id", "executionId", "mode", "trigger"}
    }
    return {
        "workflow_id": workflow_id,
        "node": raw.get("node"),
        "event_name": raw.get("event_name") or raw.get("event"),
        "payload": payload,
        "headers": raw.get("headers") or {},
        "metadata": raw.get("metadata") or {},
    }


def map_outgoing_event_to_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw = dict(payload)
    payload_data = raw.get("payload") if isinstance(raw.get("payload"), dict) else {
        key: value for key, value in raw.items() if key not in {"workflow_id", "workflowId", "node", "event_name", "eventName", "event", "headers", "metadata", "execution_id", "executionId", "mode", "trigger"}
    }
    return {
        "workflow_id": raw.get("workflow_id") or raw.get("workflowId"),
        "node": raw.get("node"),
        "event_name": raw.get("event_name") or raw.get("eventName") or raw.get("event"),
        "payload": dict(payload_data or {}),
        "headers": dict(raw.get("headers") or {}),
        "metadata": dict(raw.get("metadata") or {}),
    }


def map_event_to_webhook(event: Event | Mapping[str, Any]) -> dict[str, Any]:
    raw = _payload_dict(event)
    return {
        "workflowId": raw.get("workflow_id") or raw.get("workflowId"),
        "executionId": raw.get("execution_id") or raw.get("executionId"),
        "mode": raw.get("mode"),
        "trigger": raw.get("trigger"),
        "event": raw.get("event") or raw.get("event_name"),
        "body": raw.get("payload") or {},
        "metadata": raw.get("metadata") or {},
    }


map_inbound_event_to_webhook = map_event_to_webhook
map_message_to_event = map_send_payload_to_event
map_outgoing_payload_to_event = map_send_payload_to_event
