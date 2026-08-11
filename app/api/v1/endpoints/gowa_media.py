from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.gowa.media.exceptions import (
    GoWAMediaSendError,
    GoWAUnsupportedMedia,
    GoWAValidationError,
    sanitize_error_message,
)
from app.gowa.media.service import GoWAMediaService
from app.media.pipeline.interfaces import MediaResource

router = APIRouter()
service = GoWAMediaService()


class SendMediaRequest(BaseModel):
    """Request model for sending media via GoWA.

    The send target is identified by ``device_id`` (the GoWA device that
    owns the chat) and ``chat_id`` (the WhatsApp chat identifier).
    Connection credentials are never accepted here; authentication lives
    in the GoWA connector.
    """

    media_id: str
    device_id: str
    chat_id: str


class SendMediaResponse(BaseModel):
    """Response model for media send operations."""

    status: str
    media_id: str
    device_id: str
    chat_id: str
    message_id: str | None = None
    provider: str
    metadata: dict[str, Any] | None = None


class CapabilitiesResponse(BaseModel):
    """Response model for GoWA media capabilities."""

    supported_types: list[str]
    max_upload_size: int | None = None
    features: dict[str, bool]


@router.post("/gowa/media/send", response_model=SendMediaResponse)
async def send_media(payload: SendMediaRequest) -> SendMediaResponse:
    """Send a media resource to a WhatsApp chat via GoWA.

    The media must have been previously processed by the Media Pipeline
    and assigned a media_id. The target chat is identified by device_id
    and chat_id.
    """
    try:
        # In a real implementation, we would fetch the MediaResource from storage
        # using the media_id. For now, we'll create a mock resource.
        resource = _get_media_resource(payload.media_id)
        result = await service.send_media(resource, payload.device_id, payload.chat_id)
        return SendMediaResponse(**result)

    except GoWAValidationError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except GoWAUnsupportedMedia as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except GoWAMediaSendError as exc:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=sanitize_error_message(str(exc))) from exc
    except Exception as exc:
        detail = sanitize_error_message(f"Failed to send media: {exc}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail) from exc


@router.get("/gowa/media/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities() -> CapabilitiesResponse:
    """Return GoWA media sending capabilities."""
    return CapabilitiesResponse(
        supported_types=["photo", "video", "audio", "voice", "sticker", "document"],
        max_upload_size=None,  # Would be configured from GoWA config
        features={
            "caption": True,
            "thumbnail": True,
            "voice_note": True,
            "sticker": True,
            "document": True,
        },
    )


def _get_media_resource(media_id: str) -> MediaResource:
    """Retrieve a MediaResource by its ID.

    This is a placeholder implementation. In production, this would
    fetch the resource from the media storage system.

    Args:
        media_id: The media identifier.

    Returns:
        The MediaResource object.

    Raises:
        HTTPException: If the media resource is not found.
    """
    # Placeholder: In production, fetch from storage
    # For now, raise an error to indicate this needs implementation
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        detail="Media resource retrieval not yet implemented. Use the media pipeline to process media first.",
    )