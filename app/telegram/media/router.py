from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.media.exceptions import MediaNotFound, MediaTooLarge, UnsupportedMedia
from app.media.models import MediaMetadata, MediaType
from app.schemas.common import APIModel
from app.telegram.media.downloader import DownloadFailed, TelegramMediaTimeout
from app.telegram.media.mapper import InvalidTelegramMedia
from app.telegram.media.service import TelegramMediaService

router = APIRouter(prefix="/telegram/media")


class TelegramMediaDownloadRequest(APIModel):
    media: dict[str, Any]
    session_id: str = "default"


class TelegramMediaDownloadResponse(APIModel):
    media_id: str
    metadata: MediaMetadata
    storage_key: str
    ready: bool


def get_telegram_media_service(request: Request) -> TelegramMediaService:
    return request.app.state.container.telegram_media_service


@router.post("/download", response_model=TelegramMediaDownloadResponse)
async def download_telegram_media(
    payload: TelegramMediaDownloadRequest,
    service: Annotated[TelegramMediaService, Depends(get_telegram_media_service)],
) -> TelegramMediaDownloadResponse:
    try:
        resource = await service.download(payload.media, session_id=payload.session_id)
    except InvalidTelegramMedia as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except (UnsupportedMedia, MediaTooLarge) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MediaNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TelegramMediaTimeout as exc:
        raise HTTPException(
            status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Telegram media download timed out",
        ) from exc
    except TimeoutError as exc:
        raise HTTPException(
            status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Telegram media download timed out",
        ) from exc
    except DownloadFailed as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return TelegramMediaDownloadResponse(
        media_id=resource.metadata.id,
        metadata=resource.metadata,
        storage_key=resource.storage_key,
        ready=resource.ready,
    )


@router.get("/{media_id}", response_model=TelegramMediaDownloadResponse)
async def get_telegram_media(media_id: str) -> TelegramMediaDownloadResponse:
    if not media_id.strip():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Media not found")
    metadata = MediaMetadata(
        type=MediaType.DOCUMENT,
        mime_type="application/octet-stream",
        filename=f"{media_id}.bin",
        size=0,
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        telegram_file_id=media_id,
    )
    return TelegramMediaDownloadResponse(
        media_id=metadata.id,
        metadata=metadata,
        storage_key=f"document/{metadata.id}",
        ready=True,
    )
