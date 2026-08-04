from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from app.media.exceptions import MediaTooLarge, UnsupportedMedia
from app.media.models import Document
from app.media.providers.local import LocalStorageProvider
from app.media.utils import calculate_sha256


def _metadata(content: bytes, filename: str = "doc.txt") -> Document:
    return Document(
        mime_type="text/plain",
        filename=filename,
        size=len(content),
        sha256=calculate_sha256(content),
    )


def test_local_provider_save_load_exists_delete(tmp_path: Path) -> None:
    async def run() -> None:
        provider = LocalStorageProvider(tmp_path, max_size=100, allowed_extensions=[".txt"])
        content = b"local content"

        storage_key = await provider.save(content, _metadata(content))
        path = tmp_path / storage_key

        assert path.is_file()
        assert path.name == calculate_sha256(content)
        assert len(path.parts) >= 3
        assert await provider.exists(storage_key) is True
        assert b"".join([chunk async for chunk in provider.load(storage_key)]) == content
        assert (await provider.metadata(storage_key))["provider"] == "local"

        await provider.delete(storage_key)

        assert await provider.exists(storage_key) is False

    asyncio.run(run())


def test_local_provider_rejects_large_file(tmp_path: Path) -> None:
    async def run() -> None:
        provider = LocalStorageProvider(tmp_path, max_size=3, allowed_extensions=[".txt"])

        with pytest.raises(MediaTooLarge):
            await provider.save(b"large", _metadata(b"large"))

    asyncio.run(run())


def test_local_provider_rejects_disallowed_extension(tmp_path: Path) -> None:
    async def run() -> None:
        provider = LocalStorageProvider(tmp_path, max_size=100, allowed_extensions=[".txt"])

        with pytest.raises(UnsupportedMedia):
            await provider.save(b"content", _metadata(b"content", filename="doc.exe"))

    asyncio.run(run())


def test_local_provider_prevents_overwrite(tmp_path: Path) -> None:
    async def run() -> None:
        provider = LocalStorageProvider(tmp_path, max_size=100, allowed_extensions=[".txt"])
        content = b"same content"
        storage_key = await provider.save(content, _metadata(content))
        path = tmp_path / storage_key
        first_mtime = path.stat().st_mtime_ns

        assert await provider.save(content, _metadata(content)) == storage_key
        assert path.stat().st_mtime_ns == first_mtime

    asyncio.run(run())
