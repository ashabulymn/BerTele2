from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.events.event import Event

from .models import GoWAInboundEvent, GoWAOutboundEvent

_SUPPORTED_TYPES = {"text", "image", "audio", "video", "document", "reply"}


def _normalize_message_type(value: Any) -> str:
    normalized = str(value or "text").strip().lower()
    if normalized in {"image_url", "photo"}:
        return "image"
    if normalized in {"voice", "audio_file"}:
        return "audio"
    if normalized in {"video_file", "video_url"}:
        return "video"
    if normalized in {"document_file", "file"}:
        return "document"
    if normalized in {"reply_message", "response", "quoted"}:
        return "reply"
    if normalized not in _SUPPORTED_TYPES:
        return "text"
    return normalized


def map_event_to_webhook(event: Event | Mapping[str, Any]) -> dict[str, Any]:
    raw = event.payload if isinstance(event, Event) else dict(event)
    sender = raw.get("from_number") or raw.get("from") or raw.get("sender") or "unknown"
    recipient = raw.get("to_number") or raw.get("to") or raw.get("recipient") or raw.get("chat_id") or "unknown"
    message_type = _normalize_message_type(raw.get("message_type") or raw.get("type") or "text")
    payload: dict[str, Any] = {
        "from": str(sender),
        "to": str(recipient),
        "type": message_type,
        "text": raw.get("text") or raw.get("body"),
        "media_url": raw.get("media_url") or raw.get("file_url") or raw.get("image_url"),
        "caption": raw.get("caption"),
        "reply_to": raw.get("reply_to"),
    }
    metadata = raw.get("metadata")
    if metadata:
        payload["metadata"] = dict(metadata)
    return payload


def map_webhook_to_event(payload: Mapping[str, Any]) -> Event:
    raw = dict(payload)
    raw_type = _normalize_message_type(raw.get("type") or raw.get("message_type") or "text")
    sender = raw.get("from") or raw.get("from_number") or raw.get("sender") or "unknown"
    recipient = raw.get("to") or raw.get("recipient") or raw.get("chat_id") or "unknown"
    text = raw.get("text") or raw.get("body") or raw.get("caption")
    media_url = raw.get("media_url") or raw.get("image_url") or raw.get("file_url")
    caption = raw.get("caption")
    metadata = {k: v for k, v in raw.items() if k not in {"type", "message_type", "text", "media_url", "file_url", "caption", "to", "from", "from_number", "sender", "recipient", "chat_id", "reply_to"}}
    if raw.get("reply_to") is not None:
        metadata["reply_to"] = raw["reply_to"]
    return GoWAInboundEvent(
        from_number=str(sender),
        to_number=str(recipient),
        message_type=raw_type,
        text=text,
        media_url=media_url,
        caption=caption,
        reply_to=raw.get("reply_to"),
        metadata=metadata,
    )


def map_outgoing_event_to_message(payload: Mapping[str, Any]) -> dict[str, Any]:
    raw = dict(payload)
    message_type = _normalize_message_type(raw.get("message_type") or raw.get("type") or "text")
    recipient = raw.get("recipient") or raw.get("to")
    if recipient is None:
        raise ValueError("Outgoing GoWA payload is missing a recipient")
    metadata = dict(raw.get("metadata") or {})
    if raw.get("reply_to") is not None:
        metadata["reply_to"] = raw["reply_to"]
    send_request: dict[str, Any] = {
        "to": str(recipient),
        "type": message_type,
        "text": raw.get("text"),
        "media_url": raw.get("media_url") or raw.get("file_url"),
        "caption": raw.get("caption"),
        "reply_to": raw.get("reply_to"),
    }
    if metadata:
        send_request["metadata"] = metadata
    return {k: v for k, v in send_request.items() if v is not None}


def map_outgoing_payload_to_event(payload: Mapping[str, Any]) -> GoWAOutboundEvent:
    raw = dict(payload)
    recipient = raw.get("to") or raw.get("recipient") or "unknown"
    return GoWAOutboundEvent(
        recipient=str(recipient),
        message_type=_normalize_message_type(raw.get("type") or raw.get("message_type") or "text"),
        text=raw.get("text"),
        media_url=raw.get("media_url") or raw.get("file_url"),
        caption=raw.get("caption"),
        reply_to=raw.get("reply_to"),
        metadata=dict(raw.get("metadata") or {}),
    )


def map_inbound_event_to_webhook(event: Event | Mapping[str, Any]) -> dict[str, Any]:
    return map_event_to_webhook(event)


def map_message_to_event(payload: Mapping[str, Any]) -> GoWAOutboundEvent:
    return map_outgoing_payload_to_event(payload)


def map_event_to_message(event: Event | Mapping[str, Any]) -> dict[str, Any]:
    raw = event.payload if isinstance(event, Event) else dict(event)
    return map_outgoing_event_to_message(raw)
