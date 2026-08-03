from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.common import APIModel


class DialogPeer(APIModel):
    id: int
    type: str
    title: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_bot: bool | None = None


class DialogInfo(APIModel):
    id: int
    peer: DialogPeer
    name: str | None = None
    unread_count: int | None = None
    folder_id: int | None = None
    pinned: bool | None = None
    archived: bool | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class MessageInfo(APIModel):
    id: int
    dialog_id: int
    sender_id: int | None = None
    text: str | None = None
    date: datetime | None = None
    out: bool | None = None
    grouped_id: int | None = None
    reply_to_msg_id: int | None = None
    fwd_from: dict[str, Any] | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ListDialogsResponse(APIModel):
    items: list[DialogInfo]
    total: int
    limit: int
    offset: int


class ListMessagesResponse(APIModel):
    items: list[MessageInfo]
    total: int
    limit: int
    offset: int


class SendMessageRequest(APIModel):
    peer: str
    message: str


class SendMessageResponse(APIModel):
    message_id: int
    peer: str


class ForwardMessageRequest(APIModel):
    from_peer: str
    to_peer: str
    message_ids: list[int]


class ForwardMessageResponse(APIModel):
    message_ids: list[int]
    from_peer: str
    to_peer: str
