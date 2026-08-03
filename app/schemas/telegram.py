from __future__ import annotations

from typing import Any

from pydantic import Field

from app.schemas.common import APIModel


class UserInfo(APIModel):
    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    is_bot: bool


class DialogInfo(APIModel):
    id: int
    title: str | None = None
    name: str | None = None
    unread_count: int | None = None
    entity: dict[str, Any] = Field(default_factory=dict)


class SendMessageRequest(APIModel):
    peer: str
    message: str


class SendMessageResponse(APIModel):
    message_id: int
    peer: str

