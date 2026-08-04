from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from app.core.config import Settings, get_settings
from app.media.providers.base import StorageProvider
from app.media.providers.local import LocalStorageProvider
from app.media.providers.memory import MemoryStorageProvider


class StorageFactory:
    """Create storage providers by provider name."""

    @classmethod
    def create(
        cls,
        provider: str | None = None,
        *,
        settings: Settings | None = None,
        storage_path: str | Path | None = None,
        max_size: int | None = None,
        allowed_extensions: Iterable[str] | str | None = None,
    ) -> StorageProvider:
        settings = settings or get_settings()
        provider_name = (provider or settings.media_provider).strip().lower()

        if provider_name == "memory":
            return MemoryStorageProvider()

        if provider_name == "local":
            return LocalStorageProvider(
                storage_path=storage_path or settings.media_storage_path,
                max_size=max_size or settings.media_max_size,
                allowed_extensions=cls._parse_extensions(
                    allowed_extensions
                    if allowed_extensions is not None
                    else settings.media_allowed_extensions
                ),
            )

        raise ValueError(f"Unsupported storage provider: {provider_name}")

    @staticmethod
    def _parse_extensions(value: Iterable[str] | str) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return list(value)
