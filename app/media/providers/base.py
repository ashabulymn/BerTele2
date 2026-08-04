from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Mapping
from typing import Any

from app.media.models import MediaMetadata


class StorageProvider(ABC):
    """Interface implemented by media storage providers."""

    name: str

    @abstractmethod
    async def save(self, content: bytes, metadata: MediaMetadata | None = None) -> str:
        """Persist content and return its storage key."""

    @abstractmethod
    async def load(self, storage_key: str) -> AsyncIterator[bytes]:
        """Stream persisted content chunks for a storage key."""

    @abstractmethod
    async def delete(self, storage_key: str) -> None:
        """Delete persisted content for a storage key."""

    @abstractmethod
    async def exists(self, storage_key: str) -> bool:
        """Return whether persisted content exists for a storage key."""

    @abstractmethod
    async def get_url(self, storage_key: str) -> str:
        """Return a provider-local URL for a storage key."""

    @abstractmethod
    async def metadata(self, storage_key: str) -> Mapping[str, Any]:
        """Return provider metadata for a storage key."""
