from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from datetime import UTC, datetime
from typing import Any

from app.media.exceptions import MediaNotFound
from app.media.models import MediaMetadata
from app.media.providers.base import StorageProvider
from app.media.utils import calculate_sha256


class MemoryStorageProvider(StorageProvider):
    """In-memory storage provider for tests, development, and CI."""

    name = "memory"

    def __init__(self) -> None:
        self._objects: dict[str, bytes] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    async def save(self, content: bytes, metadata: MediaMetadata | None = None) -> str:
        storage_key = calculate_sha256(content)
        if storage_key not in self._objects:
            self._objects[storage_key] = content
            self._metadata[storage_key] = {
                "storage_key": storage_key,
                "provider": self.name,
                "size": len(content),
                "sha256": storage_key,
                "created_at": datetime.now(UTC).isoformat(),
                "media_id": metadata.id if metadata else None,
                "mime_type": metadata.mime_type if metadata else None,
                "filename": metadata.filename if metadata else None,
            }
        return storage_key

    async def load(self, storage_key: str) -> AsyncIterator[bytes]:
        if storage_key not in self._objects:
            raise MediaNotFound(f"Media content not found: {storage_key}")
        yield self._objects[storage_key]

    async def delete(self, storage_key: str) -> None:
        self._objects.pop(storage_key, None)
        self._metadata.pop(storage_key, None)

    async def exists(self, storage_key: str) -> bool:
        return storage_key in self._objects

    async def get_url(self, storage_key: str) -> str:
        if storage_key not in self._objects:
            raise MediaNotFound(f"Media content not found: {storage_key}")
        return f"memory://{storage_key}"

    async def metadata(self, storage_key: str) -> Mapping[str, Any]:
        if storage_key not in self._metadata:
            raise MediaNotFound(f"Media content not found: {storage_key}")
        return dict(self._metadata[storage_key])
