from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.media.exceptions import MediaNotFound, MediaTooLarge, UnsupportedMedia
from app.media.models import MediaMetadata
from app.media.providers.base import StorageProvider
from app.media.utils import calculate_sha256


class LocalStorageProvider(StorageProvider):
    """Filesystem-backed storage provider using sha256 content keys."""

    name = "local"

    def __init__(
        self,
        storage_path: str | Path,
        *,
        max_size: int,
        allowed_extensions: Iterable[str] | None = None,
        chunk_size: int = 1024 * 1024,
    ) -> None:
        self.storage_path = Path(storage_path)
        self.max_size = max_size
        self.allowed_extensions = self._normalize_extensions(allowed_extensions or [])
        self.chunk_size = chunk_size

    async def save(self, content: bytes, metadata: MediaMetadata | None = None) -> str:
        self._validate(content, metadata)
        sha256 = calculate_sha256(content)
        now = datetime.now(UTC)
        storage_key = f"{now:%Y}/{now:%m}/{sha256}"
        target = self.storage_path / storage_key

        if not await asyncio.to_thread(target.exists):
            await asyncio.to_thread(target.parent.mkdir, parents=True, exist_ok=True)
            await asyncio.to_thread(target.write_bytes, content)

        return storage_key

    async def load(self, storage_key: str) -> AsyncIterator[bytes]:
        path = self._resolve_key(storage_key)
        if not await asyncio.to_thread(path.is_file):
            raise MediaNotFound(f"Media content not found: {storage_key}")

        with path.open("rb") as file:
            while chunk := await asyncio.to_thread(file.read, self.chunk_size):
                yield chunk

    async def delete(self, storage_key: str) -> None:
        path = self._resolve_key(storage_key)
        if await asyncio.to_thread(path.exists):
            await asyncio.to_thread(path.unlink)

    async def exists(self, storage_key: str) -> bool:
        return await asyncio.to_thread(self._resolve_key(storage_key).is_file)

    async def get_url(self, storage_key: str) -> str:
        path = self._resolve_key(storage_key)
        if not await asyncio.to_thread(path.is_file):
            raise MediaNotFound(f"Media content not found: {storage_key}")
        return path.as_uri()

    async def metadata(self, storage_key: str) -> Mapping[str, Any]:
        path = self._resolve_key(storage_key)
        if not await asyncio.to_thread(path.is_file):
            raise MediaNotFound(f"Media content not found: {storage_key}")

        stat = await asyncio.to_thread(path.stat)
        return {
            "storage_key": storage_key,
            "provider": self.name,
            "path": str(path),
            "size": stat.st_size,
            "sha256": path.name,
            "modified_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
        }

    def _validate(self, content: bytes, metadata: MediaMetadata | None) -> None:
        if len(content) > self.max_size:
            raise MediaTooLarge(f"Media exceeds {self.max_size} bytes")

        if not self.allowed_extensions or metadata is None or metadata.filename is None:
            return

        extension = Path(metadata.filename).suffix.lower()
        if extension not in self.allowed_extensions:
            raise UnsupportedMedia(f"Unsupported media extension: {extension}")

    def _resolve_key(self, storage_key: str) -> Path:
        key_path = Path(storage_key)
        if key_path.is_absolute() or ".." in key_path.parts:
            raise MediaNotFound(f"Media content not found: {storage_key}")
        return self.storage_path / key_path

    @staticmethod
    def _normalize_extensions(extensions: Iterable[str]) -> set[str]:
        normalized: set[str] = set()
        for extension in extensions:
            value = extension.strip().lower()
            if not value:
                continue
            normalized.add(value if value.startswith(".") else f".{value}")
        return normalized
