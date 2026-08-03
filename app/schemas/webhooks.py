from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import APIModel


class WebhookFilterInfo(APIModel):
    event_name: str


class WebhookCreate(APIModel):
    name: str
    url: str
    secret: str
    is_active: bool = True
    event_names: list[str] = Field(default_factory=list)


class WebhookUpdate(APIModel):
    name: str | None = None
    url: str | None = None
    secret: str | None = None
    is_active: bool | None = None
    event_names: list[str] | None = None


class WebhookInfo(APIModel):
    id: int
    name: str
    url: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
    event_names: list[str] = Field(default_factory=list)


class WebhookListResponse(APIModel):
    items: list[WebhookInfo]
