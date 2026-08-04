from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.media.models import MediaMetadata, MediaPrepareRequest, MediaType
from app.media.service import MediaService

router = APIRouter()
service = MediaService()


@router.get("/media/types", response_model=list[str])
async def list_media_types() -> list[str]:
    """Return supported media type names."""
    return [media_type.value for media_type in MediaType]


@router.get("/media/{media_id}", response_model=MediaMetadata)
async def get_media(media_id: str) -> MediaMetadata:
    """Return mocked media metadata until persistent storage is introduced."""
    if not media_id.strip():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Media not found")

    return service.create_metadata(
        payload=MediaPrepareRequest(
            type=MediaType.DOCUMENT,
            filename=f"{media_id}.bin",
            mime_type="application/octet-stream",
            caption="Mock media metadata",
        ),
        content=b"",
    )


@router.delete("/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(media_id: str) -> None:
    """Accept a mocked delete request until persistent storage is introduced."""
    if not media_id.strip():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Media not found")
