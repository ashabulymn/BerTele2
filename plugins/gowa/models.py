from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.events.event import Event

MediaType = Literal["text", "image", "document", "audio", "video"]


class GoWAWebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    from_: str | None = Field(default=None, alias="from")
    to: str | None = None
    type: MediaType = "text"
    text: str | None = None
    media_url: str | None = None
    file_url: str | None = None
    caption: str | None = None
    mime_type: str | None = None
    filename: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def sender(self) -> str | None:
        return self.from_ or self.metadata.get("sender")


class GoWASendRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    to: str
    type: MediaType = "text"
    text: str | None = None
    media_url: str | None = None
    file_url: str | None = None
    caption: str | None = None
    mime_type: str | None = None
    filename: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GoWAInboundEvent(Event):
    def __init__(
        self,
        *,
        from_number: str,
        to_number: str,
        message_type: MediaType = "text",
        text: str | None = None,
        media_url: str | None = None,
        caption: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "from_number": from_number,
            "to_number": to_number,
            "message_type": message_type,
            "text": text,
            "media_url": media_url,
            "caption": caption,
            "metadata": metadata or {},
        }
        super().__init__(name="gowa.message.incoming", payload=payload)


class GoWAOutboundEvent(Event):
    def __init__(
        self,
        *,
        recipient: str,
        message_type: MediaType = "text",
        text: str | None = None,
        media_url: str | None = None,
        caption: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "recipient": recipient,
            "message_type": message_type,
            "text": text,
            "media_url": media_url,
            "caption": caption,
            "metadata": metadata or {},
        }
        super().__init__(name="gowa.message.outgoing", payload=payload)
