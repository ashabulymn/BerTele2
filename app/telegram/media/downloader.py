from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from app.media.exceptions import MediaNotFound, MediaTooLarge, UnsupportedMedia
from app.media.pipeline.interfaces import MediaResource
from app.media.service import MediaService
from app.telegram.media.client import TelegramMediaClient
from app.telegram.media.mapper import InvalidTelegramMedia, TelegramMediaMapper


class DownloadFailed(RuntimeError):
    """Raised when Telegram media download fails."""


class TelegramMediaTimeout(TimeoutError):
    """Raised when Telegram media download exceeds the configured timeout."""


@dataclass(slots=True)
class TelegramMediaDownloader:
    client: TelegramMediaClient
    media_service: MediaService
    mapper: TelegramMediaMapper = field(default_factory=TelegramMediaMapper)
    max_download_size: int = 50 * 1024 * 1024
    chunk_size: int = 1024 * 1024
    download_timeout: float = 30.0
    retry_count: int = 3
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger(__name__))

    async def download(self, media: Any, *, session_id: str = "default") -> MediaResource:
        try:
            mapping = self.mapper.map(media)
        except InvalidTelegramMedia:
            raise
        except Exception as exc:
            raise InvalidTelegramMedia("Invalid Telegram media") from exc

        if mapping.expected_size and mapping.expected_size > self.max_download_size:
            raise MediaTooLarge(f"Telegram media exceeds {self.max_download_size} bytes")

        await self._get_file_metadata(mapping.file_reference, session_id=session_id)
        resource = await asyncio.wait_for(
            self._download_mapped(mapping, session_id=session_id),
            timeout=self.download_timeout,
        )
        return resource

    async def _get_file_metadata(self, file_reference: Any, *, session_id: str) -> Any:
        try:
            metadata = await self.client.get_file_metadata(file_reference, session_id=session_id)
        except Exception as exc:
            raise MediaNotFound("Telegram media file was not found") from exc
        if metadata is None:
            raise MediaNotFound("Telegram media file was not found")
        return metadata

    async def _download_mapped(self, mapping, *, session_id: str) -> MediaResource:
        last_error: Exception | None = None
        for attempt in range(1, self.retry_count + 1):
            try:
                return await self._stream_to_metadata(mapping, session_id=session_id)
            except (TimeoutError, MediaTooLarge, UnsupportedMedia, InvalidTelegramMedia):
                raise
            except Exception as exc:
                last_error = exc
                self.logger.warning("Telegram media download attempt %s failed", attempt)
        raise DownloadFailed("Telegram media download failed") from last_error

    async def _stream_to_metadata(self, mapping, *, session_id: str) -> MediaResource:
        total_size = 0
        chunks: list[bytes] = []

        async for chunk in self.client.stream_file(
            mapping.file_reference,
            chunk_size=self.chunk_size,
            session_id=session_id,
        ):
            total_size += len(chunk)
            if total_size > self.max_download_size:
                raise MediaTooLarge(f"Telegram media exceeds {self.max_download_size} bytes")
            chunks.append(chunk)

        payload = mapping.payload.model_copy(
            update={"mime_type": mapping.mime_type or mapping.payload.mime_type}
        )
        return await self.media_service.process(
            payload,
            b"".join(chunks),
            connector="telegram",
            source=str(mapping.file_reference),
        )
