from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import Field

from app.schemas.common import APIModel


class MediaType(StrEnum):
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    STICKER = "sticker"
    ANIMATION = "animation"
    DOCUMENT = "document"


class MediaMetadata(APIModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: MediaType
    mime_type: str
    filename: str | None = None
    caption: str | None = None
    size: int
    width: int | None = None
    height: int | None = None
    duration: float | None = None
    sha256: str
    telegram_file_id: str | None = None
    thumbnail_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Photo(MediaMetadata):
    type: MediaType = MediaType.PHOTO


class Video(MediaMetadata):
    type: MediaType = MediaType.VIDEO


class Audio(MediaMetadata):
    type: MediaType = MediaType.AUDIO


class Voice(MediaMetadata):
    type: MediaType = MediaType.VOICE


class Sticker(MediaMetadata):
    type: MediaType = MediaType.STICKER


class Animation(MediaMetadata):
    type: MediaType = MediaType.ANIMATION


class Document(MediaMetadata):
    type: MediaType = MediaType.DOCUMENT


MEDIA_MODEL_BY_TYPE: dict[MediaType, type[MediaMetadata]] = {
    MediaType.PHOTO: Photo,
    MediaType.VIDEO: Video,
    MediaType.AUDIO: Audio,
    MediaType.VOICE: Voice,
    MediaType.STICKER: Sticker,
    MediaType.ANIMATION: Animation,
    MediaType.DOCUMENT: Document,
}


class MediaPrepareRequest(APIModel):
    type: MediaType
    filename: str | None = None
    caption: str | None = None
    mime_type: str | None = None
    width: int | None = None
    height: int | None = None
    duration: float | None = None
    telegram_file_id: str | None = None
    thumbnail_id: str | None = None


class MediaOperation(APIModel):
    media_id: str
    metadata: MediaMetadata
    storage_key: str
    ready: bool = True
