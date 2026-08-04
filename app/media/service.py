from __future__ import annotations

from dataclasses import dataclass

from app.media.exceptions import MediaTooLarge, UnsupportedMedia
from app.media.models import MEDIA_MODEL_BY_TYPE, MediaMetadata, MediaOperation, MediaPrepareRequest, MediaType
from app.media.utils import calculate_sha256, detect_mime_type, sanitize_filename

DEFAULT_MAX_MEDIA_SIZE = 50 * 1024 * 1024

SUPPORTED_MIME_PREFIXES: dict[MediaType, tuple[str, ...]] = {
    MediaType.PHOTO: ("image/",),
    MediaType.VIDEO: ("video/",),
    MediaType.AUDIO: ("audio/",),
    MediaType.VOICE: ("audio/",),
    MediaType.STICKER: ("image/", "application/x-tgsticker"),
    MediaType.ANIMATION: ("image/gif", "video/"),
    MediaType.DOCUMENT: ("application/", "text/", "image/", "audio/", "video/"),
}


@dataclass(slots=True)
class MediaService:
    """Prepare and validate media metadata without transferring content."""

    max_media_size: int = DEFAULT_MAX_MEDIA_SIZE

    def validate_media(self, media_type: MediaType, content: bytes, mime_type: str) -> None:
        """Validate media size and mime compatibility."""
        if len(content) > self.max_media_size:
            raise MediaTooLarge(f"Media exceeds {self.max_media_size} bytes")

        supported_prefixes = SUPPORTED_MIME_PREFIXES[media_type]
        if not any(mime_type == prefix.rstrip("/") or mime_type.startswith(prefix) for prefix in supported_prefixes):
            raise UnsupportedMedia(f"Unsupported mime type for {media_type}: {mime_type}")

    def create_metadata(self, payload: MediaPrepareRequest, content: bytes) -> MediaMetadata:
        """Create typed media metadata from a preparation request and content bytes."""
        filename = sanitize_filename(payload.filename) if payload.filename else None
        mime_type = payload.mime_type or detect_mime_type(filename, content)
        self.validate_media(payload.type, content, mime_type)

        model = MEDIA_MODEL_BY_TYPE[payload.type]
        return model(
            mime_type=mime_type,
            filename=filename,
            caption=payload.caption,
            size=len(content),
            width=payload.width,
            height=payload.height,
            duration=payload.duration,
            sha256=calculate_sha256(content),
            telegram_file_id=payload.telegram_file_id,
            thumbnail_id=payload.thumbnail_id,
        )

    def create_streamed_metadata(
        self,
        payload: MediaPrepareRequest,
        *,
        size: int,
        sha256: str,
        mime_type: str,
        sample: bytes = b"",
    ) -> MediaMetadata:
        """Create metadata for content that was hashed while streaming."""
        filename = sanitize_filename(payload.filename) if payload.filename else None
        detected_mime_type = mime_type or payload.mime_type or detect_mime_type(filename, sample)
        self.validate_media(payload.type, sample[: min(len(sample), self.max_media_size + 1)], detected_mime_type)
        if size > self.max_media_size:
            raise MediaTooLarge(f"Media exceeds {self.max_media_size} bytes")

        model = MEDIA_MODEL_BY_TYPE[payload.type]
        return model(
            mime_type=detected_mime_type,
            filename=filename,
            caption=payload.caption,
            size=size,
            width=payload.width,
            height=payload.height,
            duration=payload.duration,
            sha256=sha256,
            telegram_file_id=payload.telegram_file_id,
            thumbnail_id=payload.thumbnail_id,
        )

    def prepare_upload(self, payload: MediaPrepareRequest, content: bytes) -> MediaOperation:
        """Prepare metadata and a deterministic storage key for a future upload."""
        metadata = self.create_metadata(payload, content)
        return MediaOperation(
            media_id=metadata.id,
            metadata=metadata,
            storage_key=f"{metadata.type}/{metadata.id}",
        )

    def prepare_download(self, metadata: MediaMetadata) -> MediaOperation:
        """Prepare a download operation descriptor for already known metadata."""
        return MediaOperation(
            media_id=metadata.id,
            metadata=metadata,
            storage_key=f"{metadata.type}/{metadata.id}",
        )
