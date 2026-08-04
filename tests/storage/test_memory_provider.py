from __future__ import annotations

import asyncio

from app.media.models import Document
from app.media.providers.memory import MemoryStorageProvider
from app.media.utils import calculate_sha256


def test_memory_provider_save_load_exists_delete() -> None:
    async def run() -> None:
        provider = MemoryStorageProvider()
        content = b"hello storage"
        metadata = Document(mime_type="text/plain", filename="note.txt", size=len(content), sha256=calculate_sha256(content))

        storage_key = await provider.save(content, metadata)

        assert await provider.exists(storage_key) is True
        assert b"".join([chunk async for chunk in provider.load(storage_key)]) == content
        assert await provider.get_url(storage_key) == f"memory://{storage_key}"
        assert (await provider.metadata(storage_key))["media_id"] == metadata.id

        await provider.delete(storage_key)

        assert await provider.exists(storage_key) is False

    asyncio.run(run())
