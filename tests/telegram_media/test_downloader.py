from __future__ import annotations

import hashlib
from collections.abc import AsyncIterator

import pytest

from app.media.exceptions import MediaNotFound, MediaTooLarge
from app.media.models import MediaType
from app.media.providers.memory import MemoryStorageProvider
from app.media.service import MediaService
from app.telegram.media.downloader import DownloadFailed, TelegramMediaDownloader


class FakeTelegramMediaClient:
    def __init__(
        self,
        chunks: list[bytes],
        *,
        metadata=object(),
        fail_stream: bool = False,
    ) -> None:
        self.chunks = chunks
        self.metadata = metadata
        self.fail_stream = fail_stream
        self.requested_chunk_size: int | None = None

    async def get_file_metadata(self, file_reference, *, session_id: str = "default"):
        return self.metadata

    async def stream_file(
        self,
        file_reference,
        *,
        chunk_size: int,
        session_id: str = "default",
    ) -> AsyncIterator[bytes]:
        self.requested_chunk_size = chunk_size
        if self.fail_stream:
            raise RuntimeError("download exploded")
        for chunk in self.chunks:
            yield chunk


@pytest.fixture()
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_downloader_hashes_streamed_content() -> None:
    content = [b"%PDF-", b"1.7 document"]
    client = FakeTelegramMediaClient(content)
    downloader = TelegramMediaDownloader(
        client=client,
        media_service=MediaService(max_media_size=100, storage_provider=MemoryStorageProvider()),
        chunk_size=4,
    )

    resource = await downloader.download(
        {
            "type": "document",
            "file_reference": "doc-ref",
            "filename": "doc.pdf",
            "size": sum(len(chunk) for chunk in content),
        }
    )

    expected_hash = hashlib.sha256(b"".join(content)).hexdigest()
    assert resource.metadata.sha256 == expected_hash
    assert resource.metadata.type == MediaType.DOCUMENT
    assert resource.metadata.mime_type == "application/pdf"
    assert resource.storage_key == expected_hash
    assert client.requested_chunk_size == 4


@pytest.mark.anyio
async def test_downloader_rejects_large_file_before_download() -> None:
    downloader = TelegramMediaDownloader(
        client=FakeTelegramMediaClient([b"ignored"]),
        media_service=MediaService(max_media_size=3, storage_provider=MemoryStorageProvider()),
        max_download_size=3,
    )

    with pytest.raises(MediaTooLarge):
        await downloader.download({"type": "document", "file_reference": "doc-ref", "size": 4})


@pytest.mark.anyio
async def test_downloader_rejects_large_file_while_streaming() -> None:
    downloader = TelegramMediaDownloader(
        client=FakeTelegramMediaClient([b"12", b"34"]),
        media_service=MediaService(max_media_size=3, storage_provider=MemoryStorageProvider()),
        max_download_size=3,
    )

    with pytest.raises(MediaTooLarge):
        await downloader.download({"type": "document", "file_reference": "doc-ref"})


@pytest.mark.anyio
async def test_downloader_raises_media_not_found_for_missing_metadata() -> None:
    downloader = TelegramMediaDownloader(
        client=FakeTelegramMediaClient([b"content"], metadata=None),
        media_service=MediaService(storage_provider=MemoryStorageProvider()),
    )

    with pytest.raises(MediaNotFound):
        await downloader.download({"type": "document", "file_reference": "missing"})


@pytest.mark.anyio
async def test_downloader_reports_download_failure() -> None:
    downloader = TelegramMediaDownloader(
        client=FakeTelegramMediaClient([b"content"], fail_stream=True),
        media_service=MediaService(storage_provider=MemoryStorageProvider()),
        retry_count=1,
    )

    with pytest.raises(DownloadFailed):
        await downloader.download({"type": "document", "file_reference": "doc-ref"})
