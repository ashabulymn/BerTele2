from __future__ import annotations

from pathlib import Path

import pytest

from app.media.providers.factory import StorageFactory
from app.media.providers.local import LocalStorageProvider
from app.media.providers.memory import MemoryStorageProvider


def test_factory_creates_memory_provider() -> None:
    provider = StorageFactory.create("memory")

    assert isinstance(provider, MemoryStorageProvider)


def test_factory_creates_local_provider(tmp_path: Path) -> None:
    provider = StorageFactory.create(
        "local",
        storage_path=tmp_path,
        max_size=12,
        allowed_extensions=".txt,.pdf",
    )

    assert isinstance(provider, LocalStorageProvider)
    assert provider.storage_path == tmp_path
    assert provider.max_size == 12
    assert provider.allowed_extensions == {".txt", ".pdf"}


def test_factory_rejects_unknown_provider() -> None:
    with pytest.raises(ValueError):
        StorageFactory.create("minio")
