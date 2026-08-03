from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.events.event import Event

MediaType = Literal["text", "image", "audio", "video", "document", "reply"]


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
    reply_to: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def sender(self) -> str | None:
        return self.from_ or self.metadata.get("sender")

    @model_validator(mode="after")
    def validate_content(self) -> GoWAWebhookPayload:
        if self.type == "text" and not self.text and not self.caption and not self.reply_to:
            raise ValueError("Text GoWA messages require text, caption or reply_to")
        if self.type in {"image", "audio", "video", "document"} and not (self.media_url or self.file_url):
            raise ValueError(f"GoWA {self.type} payload requires media_url or file_url")
        if self.type == "reply" and not (self.reply_to or self.text or self.metadata.get("reply_to")):
            raise ValueError("Reply GoWA messages require reply_to or text")
        return self


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
    reply_to: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_content(self) -> GoWASendRequest:
        if self.type == "text" and not self.text and not self.caption and not self.reply_to:
            raise ValueError("Text GoWA messages require text, caption or reply_to")
        if self.type in {"image", "audio", "video", "document"} and not (self.media_url or self.file_url):
            raise ValueError(f"GoWA {self.type} payload requires media_url or file_url")
        if self.type == "reply" and not (self.reply_to or self.text or self.metadata.get("reply_to")):
            raise ValueError("Reply GoWA messages require reply_to or text")
        return self


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
        reply_to: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "from_number": from_number,
            "to_number": to_number,
            "message_type": message_type,
            "text": text,
            "media_url": media_url,
            "caption": caption,
            "reply_to": reply_to,
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
        reply_to: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        payload = {
            "recipient": recipient,
            "message_type": message_type,
            "text": text,
            "media_url": media_url,
            "caption": caption,
            "reply_to": reply_to,
            "metadata": metadata or {},
        }
        super().__init__(name="gowa.message.outgoing", payload=payload)
