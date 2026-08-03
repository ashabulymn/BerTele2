from __future__ import annotations

from datetime import datetime

from app.schemas.common import APIModel


class SessionCreate(APIModel):
    name: str
    api_id: int
    api_hash: str
    session_string: str | None = None
    phone_number: str | None = None
    bot_token: str | None = None


class SessionInfo(APIModel):
    id: int
    name: str
    api_id: int
    api_hash: str
    session_string: str | None = None
    phone_number: str | None = None
    bot_token: str | None = None
    state: str
    last_error: str | None = None
    last_connected_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None


class SessionListResponse(APIModel):
    items: list[SessionInfo]

