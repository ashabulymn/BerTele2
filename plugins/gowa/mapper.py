from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.events.event import Event

from .models import GoWAInboundEvent, GoWAOutboundEvent


def map_webhook_to_event(payload: Mapping[str, Any]) -> Event:
    raw = dict(payload)
    raw_type = raw.get("type") or raw.get("message_type") or "text"
    sender = raw.get("from") or raw.get("from_number") or raw.get("sender") or "unknown"
    recipient = raw.get("to") or raw.get("recipient") or raw.get("chat_id") or "unknown"
    text = raw.get("text") or raw.get("body") or raw.get("caption")
    media_url = raw.get("media_url") or raw.get("image_url") or raw.get("file_url")
    caption = raw.get("caption")
    return GoWAInboundEvent(
        from_number=str(sender),
        to_number=str(recipient),
        message_type=str(raw_type),
        text=text,
        media_url=media_url,
        caption=caption,
        metadata={k: v for k, v in raw.items() if k not in {"type", "message_type", "text", "media_url", "file_url", "caption", "to", "from", "from_number", "sender", "recipient", "chat_id"}},
    )


def map_outgoing_event_to_message(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw = dict(payload)
    message_type = raw.get("message_type") or raw.get("type") or "text"
    recipient = raw.get("recipient") or raw.get("to")
    if recipient is None:
        raise ValueError("Outgoing GoWA payload is missing a recipient")
    send_request = {
        "to": str(recipient),
        "type": str(message_type),
        "text": raw.get("text"),
        "media_url": raw.get("media_url") or raw.get("file_url"),
        "caption": raw.get("caption"),
    }
    if raw.get("metadata"):
        send_request["metadata"] = raw.get("metadata")
    return send_request


def map_outgoing_payload_to_event(payload: Mapping[str, Any]) -> GoWAOutboundEvent:
    raw = dict(payload)
    return GoWAOutboundEvent(
        recipient=str(raw.get("to") or raw.get("recipient") or "unknown"),
        message_type=str(raw.get("type") or raw.get("message_type") or "text"),
        text=raw.get("text"),
        media_url=raw.get("media_url") or raw.get("file_url"),
        caption=raw.get("caption"),
        metadata=dict(raw.get("metadata") or {}),
    )
