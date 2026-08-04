from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.media.models import MediaPrepareRequest, MediaType


class InvalidTelegramMedia(ValueError):
    """Raised when a Telegram media object cannot be mapped."""


@dataclass(slots=True)
class TelegramMediaMapping:
    payload: MediaPrepareRequest
    file_reference: Any
    expected_size: int | None = None
    mime_type: str | None = None


class TelegramMediaMapper:
    """Map Telegram media objects into Media Engine preparation requests."""

    def map(self, media: Any, *, caption: str | None = None) -> TelegramMediaMapping:
        media_type = self._detect_type(media)
        file_reference = self._value(media, "file_reference", "file_id", "id")
        if file_reference is None:
            raise InvalidTelegramMedia("Telegram media is missing a file reference")

        mime_type = self._value(media, "mime_type") or self._default_mime_type(media_type)
        payload = MediaPrepareRequest(
            type=media_type,
            filename=self._value(media, "file_name", "filename", "name"),
            caption=caption or self._value(media, "caption"),
            mime_type=mime_type,
            width=self._value(media, "width", "w"),
            height=self._value(media, "height", "h"),
            duration=self._value(media, "duration"),
            telegram_file_id=str(self._value(media, "file_id", "id", "file_reference")),
            thumbnail_id=self._value(media, "thumbnail_id", "thumb_id"),
        )
        return TelegramMediaMapping(
            payload=payload,
            file_reference=file_reference,
            expected_size=self._value(media, "size", "file_size"),
            mime_type=mime_type,
        )

    def _detect_type(self, media: Any) -> MediaType:
        raw_type = self._value(media, "type", "media_type", "_")
        if isinstance(raw_type, MediaType):
            return raw_type
        if isinstance(raw_type, str):
            normalized = (
                raw_type.lower()
                .removeprefix("messagemedia")
                .removeprefix("documentattribute")
            )
            aliases = {
                "photo": MediaType.PHOTO,
                "video": MediaType.VIDEO,
                "document": MediaType.DOCUMENT,
                "audio": MediaType.AUDIO,
                "voice": MediaType.VOICE,
                "animation": MediaType.ANIMATION,
                "gif": MediaType.ANIMATION,
                "sticker": MediaType.STICKER,
            }
            for marker, media_type in aliases.items():
                if marker in normalized:
                    return media_type

        if self._value(media, "voice"):
            return MediaType.VOICE
        if self._value(media, "video"):
            return MediaType.VIDEO
        if self._value(media, "round_message"):
            return MediaType.VIDEO
        if self._value(media, "animated"):
            return MediaType.ANIMATION
        if self._value(media, "sticker"):
            return MediaType.STICKER
        if self._value(media, "mime_type", default="").startswith("audio/"):
            return MediaType.AUDIO
        if self._value(media, "mime_type", default="").startswith("image/"):
            return MediaType.PHOTO
        raise InvalidTelegramMedia("Unsupported Telegram media type")

    def _default_mime_type(self, media_type: MediaType) -> str | None:
        return {
            MediaType.PHOTO: "image/jpeg",
            MediaType.VOICE: "audio/ogg",
            MediaType.STICKER: "image/webp",
        }.get(media_type)

    def _value(self, media: Any, *names: str, default: Any = None) -> Any:
        for name in names:
            if isinstance(media, dict) and name in media:
                return media[name]
            if hasattr(media, name):
                return getattr(media, name)
        return default
