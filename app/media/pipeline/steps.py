from __future__ import annotations

from dataclasses import dataclass

from app.media.models import MEDIA_MODEL_BY_TYPE
from app.media.pipeline.context import MediaPipelineContext
from app.media.pipeline.interfaces import MediaPipelineStep
from app.media.utils import calculate_sha256, detect_mime_type, sanitize_filename
from app.media.exceptions import MediaTooLarge, UnsupportedMedia

DEFAULT_MAX_MEDIA_SIZE = 50 * 1024 * 1024

SUPPORTED_MIME_PREFIXES = {
    "photo": ("image/",),
    "video": ("video/",),
    "audio": ("audio/",),
    "voice": ("audio/",),
    "sticker": ("image/", "application/x-tgsticker"),
    "animation": ("image/gif", "video/"),
    "document": ("application/", "text/", "image/", "audio/", "video/"),
}


@dataclass(slots=True)
class ValidationStep(MediaPipelineStep):
    name: str = "validation"

    async def execute(self, context: MediaPipelineContext) -> None:
        max_size = int(context.configuration.get("max_media_size", DEFAULT_MAX_MEDIA_SIZE))
        if len(context.content) > max_size:
            raise MediaTooLarge(f"Media exceeds {max_size} bytes")


@dataclass(slots=True)
class HashStep(MediaPipelineStep):
    name: str = "hash"

    async def execute(self, context: MediaPipelineContext) -> None:
        context.sha256 = calculate_sha256(context.content)


@dataclass(slots=True)
class MimeDetectionStep(MediaPipelineStep):
    name: str = "mime_detection"

    async def execute(self, context: MediaPipelineContext) -> None:
        context.mime_type = context.payload.mime_type or detect_mime_type(
            context.payload.filename,
            context.content[:4096],
        )
        prefixes = SUPPORTED_MIME_PREFIXES[context.payload.type.value]
        if not any(context.mime_type == prefix.rstrip("/") or context.mime_type.startswith(prefix) for prefix in prefixes):
            raise UnsupportedMedia(f"Unsupported mime type for {context.payload.type}: {context.mime_type}")


@dataclass(slots=True)
class MetadataStep(MediaPipelineStep):
    name: str = "metadata"

    async def execute(self, context: MediaPipelineContext) -> None:
        model = MEDIA_MODEL_BY_TYPE[context.payload.type]
        context.media_metadata = model(
            mime_type=context.mime_type or context.payload.mime_type or detect_mime_type(
                context.payload.filename,
                context.content[:4096],
            ),
            filename=sanitize_filename(context.payload.filename) if context.payload.filename else None,
            caption=context.payload.caption,
            size=len(context.content),
            width=context.payload.width,
            height=context.payload.height,
            duration=context.payload.duration,
            sha256=context.sha256 or calculate_sha256(context.content),
            telegram_file_id=context.payload.telegram_file_id,
            thumbnail_id=context.payload.thumbnail_id,
        )


@dataclass(slots=True)
class StorageStep(MediaPipelineStep):
    name: str = "storage"

    async def execute(self, context: MediaPipelineContext) -> None:
        if context.media_metadata is None:
            raise RuntimeError("Media metadata must be generated before storage")
        context.storage_key = await context.storage_provider.save(context.content, context.media_metadata)


DEFAULT_PIPELINE_STEPS: tuple[MediaPipelineStep, ...] = (
    ValidationStep(),
    HashStep(),
    MimeDetectionStep(),
    MetadataStep(),
    StorageStep(),
)
