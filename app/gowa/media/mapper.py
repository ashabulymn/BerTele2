from __future__ import annotations

import logging
from typing import Any

from app.gowa.media.exceptions import GoWAUnsupportedMedia
from app.media.models import MediaMetadata, MediaType
from app.media.pipeline.interfaces import MediaResource
from plugins.gowa.models import MediaType as GoWAMediaType

logger = logging.getLogger("app.gowa.media.media_mapper")


def map_media_resource_to_gowa_payload(resource: MediaResource) -> dict[str, Any]:
    """Map a MediaResource to a GoWA media payload.

    The mapper only includes essential fields required for sending media.
    All media processing (hash calculation, thumbnail generation, etc.)
    should be done by the MediaPipeline before the resource reaches this point.

    Args:
        resource: The media resource from the pipeline.

    Returns:
        A dictionary suitable for sending via the GoWA connector.

    Raises:
        GoWAUnsupportedMedia: If the media type is not supported by GoWA.
    """
    metadata = resource.metadata
    gowa_type = _map_media_type(metadata.type)

    payload: dict[str, Any] = {
        "type": gowa_type,
        "to": "",  # Must be set by caller
        "media_url": resource.storage_key,
        "mime_type": metadata.mime_type,
        "filename": metadata.filename,
        "caption": metadata.caption,
        "metadata": {
            "media_id": metadata.id,
            "size": metadata.size,
            "created_at": metadata.created_at.isoformat(),
        },
    }

    # Include optional metadata fields if they exist
    if metadata.width and metadata.height:
        payload["metadata"]["dimensions"] = {"width": metadata.width, "height": metadata.height}

    if metadata.duration is not None:
        payload["metadata"]["duration"] = metadata.duration

    logger.debug(
        "Mapped media resource to GoWA payload",
        extra={
            "media_id": metadata.id,
            "media_type": metadata.type.value,
            "gowa_type": gowa_type,
            "storage_key": resource.storage_key,
        },
    )

    return payload


def _map_media_type(media_type: MediaType) -> GoWAMediaType:
    """Map BerTele2 media type to GoWA media type.

    Args:
        media_type: The BerTele2 media type.

    Returns:
        The corresponding GoWA media type.

    Raises:
        GoWAUnsupportedMedia: If the media type is not supported.
    """
    type_mapping: dict[MediaType, GoWAMediaType] = {
        MediaType.PHOTO: "image",
        MediaType.VIDEO: "video",
        MediaType.AUDIO: "audio",
        MediaType.VOICE: "audio",
        MediaType.STICKER: "image",
        MediaType.ANIMATION: "video",
        MediaType.DOCUMENT: "document",
    }

    if media_type not in type_mapping:
        raise GoWAUnsupportedMedia(f"Unsupported media type: {media_type.value}")

    return type_mapping[media_type]