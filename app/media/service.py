from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.media.exceptions import MediaTooLarge, UnsupportedMedia
from app.media.models import MEDIA_MODEL_BY_TYPE, MediaMetadata, MediaOperation, MediaPrepareRequest, MediaType
from app.media.providers.base import StorageProvider
from app.media.providers.factory import StorageFactory
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
    storage_provider: StorageProvider | None = None

    def __post_init__(self) -> None:
        if self.storage_provider is None:
            self.storage_provider = StorageFactory.create(max_size=self.max_media_size)

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

    async def save(self, payload: MediaPrepareRequest, content: bytes) -> MediaOperation:
        """Validate metadata, store content, and return an upload operation descriptor."""
        metadata = self.create_metadata(payload, content)
        storage_key = await self._provider.save(content, metadata)
        return MediaOperation(media_id=metadata.id, metadata=metadata, storage_key=storage_key)

    async def load(self, storage_key: str) -> bytes:
        """Load content bytes through the configured storage provider."""
        chunks = [chunk async for chunk in self._provider.load(storage_key)]
        return b"".join(chunks)

    async def delete(self, storage_key: str) -> None:
        """Delete content through the configured storage provider."""
        await self._provider.delete(storage_key)

    async def exists(self, storage_key: str) -> bool:
        """Return whether content exists through the configured storage provider."""
        return await self._provider.exists(storage_key)

    async def storage_info(self) -> dict[str, Any]:
        """Return service-visible storage provider information."""
        provider = self._provider
        info: dict[str, Any] = {"provider": provider.name}
        storage_path = getattr(provider, "storage_path", None)
        if storage_path is not None:
            info["storage_path"] = str(storage_path)
        max_size = getattr(provider, "max_size", None)
        if max_size is not None:
            info["max_size"] = max_size
        allowed_extensions = getattr(provider, "allowed_extensions", None)
        if allowed_extensions is not None:
            info["allowed_extensions"] = sorted(allowed_extensions)
        return info

    def storage_provider_name(self) -> str:
        """Return the configured storage provider name."""
        return self._provider.name

    @property
    def _provider(self) -> StorageProvider:
        if self.storage_provider is None:
            raise RuntimeError("Storage provider is not configured")
        return self.storage_provider
