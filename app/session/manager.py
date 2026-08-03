from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

from fastapi import HTTPException, status
from telethon import TelegramClient
from telethon.sessions import StringSession

from app.session.cache import SessionCache
from app.session.model import SessionRecord, SessionState
from app.session.repository import SessionRepository


@dataclass
class SessionManager:
    repository: SessionRepository
    logger: logging.Logger
    cache: SessionCache = field(default_factory=SessionCache)
    _clients: dict[int, TelegramClient] = field(default_factory=dict, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    def _build_client(self, record: SessionRecord) -> TelegramClient:
        return TelegramClient(StringSession(record.session_string or ""), record.api_id, record.api_hash)

    def _touch(self, record: SessionRecord, *, state: SessionState, error: str | None = None) -> None:
        record.state = state
        record.last_error = error
        if state == SessionState.connected:
            record.last_connected_at = datetime.now(UTC)

    async def list_sessions(self) -> list[SessionRecord]:
        records = await self.repository.list()
        for record in records:
            self.cache.set(record)
        return records

    async def get_session(self, session_id: int) -> SessionRecord:
        cached = self.cache.get(session_id)
        if cached is not None:
            return cached
        record = await self.repository.get(session_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        self.cache.set(record)
        return record

    async def create_session(
        self,
        *,
        name: str,
        api_id: int,
        api_hash: str,
        session_string: str | None = None,
        phone_number: str | None = None,
        bot_token: str | None = None,
    ) -> SessionRecord:
        record = SessionRecord(
            name=name,
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string,
            phone_number=phone_number,
            bot_token=bot_token,
            state=SessionState.disconnected,
        )
        record = await self.repository.create(record)
        self.cache.set(record)
        return record

    async def delete_session(self, session_id: int) -> None:
        record = await self.get_session(session_id)
        await self.disconnect(session_id)
        await self.repository.delete(record)
        self.cache.delete(session_id)

    async def connect(self, session_id: int) -> SessionRecord:
        record = await self.get_session(session_id)
        async with self._lock:
            client = self._clients.get(session_id) or self._build_client(record)
            self._clients[session_id] = client
            self._touch(record, state=SessionState.reconnecting)
            try:
                if not client.is_connected():
                    await client.connect()
                self._touch(record, state=SessionState.connected)
            except Exception as exc:
                self._touch(record, state=SessionState.error, error=str(exc))
                raise
        await self.repository.session.commit()
        return record

    async def disconnect(self, session_id: int) -> SessionRecord:
        record = await self.get_session(session_id)
        async with self._lock:
            client = self._clients.get(session_id)
            if client is not None and client.is_connected():
                await client.disconnect()
            self._touch(record, state=SessionState.disconnected)
        await self.repository.session.commit()
        return record

    async def reconnect(self, session_id: int) -> SessionRecord:
        await self.disconnect(session_id)
        return await self.connect(session_id)
