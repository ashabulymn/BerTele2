from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.core.config import Settings
from app.media.service import MediaService
from app.services.telegram_service import TelegramService
from app.telegram.media.client import TelethonMediaClient, TelegramMediaClient
from app.telegram.media.downloader import MediaResource, TelegramMediaDownloader


@dataclass(slots=True)
class TelegramMediaService:
    downloader: TelegramMediaDownloader

    async def download(self, media: Any, *, session_id: str = "default") -> MediaResource:
        return await self.downloader.download(media, session_id=session_id)


def build_telegram_media_service(
    *,
    settings: Settings,
    telegram_service: TelegramService,
    client: TelegramMediaClient | None = None,
    logger: logging.Logger | None = None,
) -> TelegramMediaService:
    media_service = MediaService(max_media_size=settings.telegram_media_max_download_size)
    media_client = client or TelethonMediaClient(telegram_service.engine.client_pool)
    downloader = TelegramMediaDownloader(
        client=media_client,
        media_service=media_service,
        max_download_size=settings.telegram_media_max_download_size,
        chunk_size=settings.telegram_media_chunk_size,
        download_timeout=settings.telegram_media_download_timeout,
        retry_count=settings.telegram_media_retry_count,
        logger=logger or logging.getLogger(__name__),
    )
    return TelegramMediaService(downloader=downloader)
