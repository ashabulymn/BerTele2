from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.media.models import MediaMetadata


class MediaStorageProvider(ABC):
    """Abstract interface for future media storage providers."""

    @abstractmethod
    async def save(self, metadata: MediaMetadata, content: bytes) -> str:
        """Persist content and return a storage key."""

    @abstractmethod
    async def load(self, media_id: str) -> AsyncIterator[bytes]:
        """Stream persisted content chunks for a media id."""

    @abstractmethod
    async def delete(self, media_id: str) -> None:
        """Delete persisted content for a media id."""

    @abstractmethod
    async def exists(self, media_id: str) -> bool:
        """Return whether persisted content exists for a media id."""
