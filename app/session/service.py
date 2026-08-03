from __future__ import annotations

from dataclasses import dataclass

from app.session.manager import SessionManager


@dataclass
class SessionService:
    manager: SessionManager

    async def list_sessions(self):
        return await self.manager.list_sessions()

    async def get_session(self, session_id: int):
        return await self.manager.get_session(session_id)

    async def create_session(self, **kwargs):
        return await self.manager.create_session(**kwargs)

    async def delete_session(self, session_id: int) -> None:
        await self.manager.delete_session(session_id)

    async def connect(self, session_id: int):
        return await self.manager.connect(session_id)

    async def disconnect(self, session_id: int):
        return await self.manager.disconnect(session_id)

    async def reconnect(self, session_id: int):
        return await self.manager.reconnect(session_id)

