from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Protocol

from app.telegram.client import TelegramClientPool


class TelegramMediaClient(Protocol):
    async def get_file_metadata(self, file_reference: Any, *, session_id: str = "default") -> Any:
        """Return Telegram file metadata for a file reference."""

    async def stream_file(
        self,
        file_reference: Any,
        *,
        chunk_size: int,
        session_id: str = "default",
    ) -> AsyncIterator[bytes]:
        """Yield file content chunks from Telegram."""


@dataclass(slots=True)
class TelethonMediaClient:
    client_pool: TelegramClientPool

    async def get_file_metadata(self, file_reference: Any, *, session_id: str = "default") -> Any:
        async def operation(client):
            return await client.get_file(file_reference)

        return await self.client_pool.call(
            operation,
            action="get telegram media file",
            session_id=session_id,
        )

    async def stream_file(
        self,
        file_reference: Any,
        *,
        chunk_size: int,
        session_id: str = "default",
    ) -> AsyncIterator[bytes]:
        client = self.client_pool.client(session_id)
        async for chunk in client.iter_download(file_reference, request_size=chunk_size):
            if chunk:
                yield bytes(chunk)
