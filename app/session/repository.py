from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.session.model import SessionRecord


class SessionRepository:
    def __init__(self, storage) -> None:
        self.storage = storage

    @property
    def session(self) -> AsyncSession:
        return self.storage.session

    async def list(self) -> list[SessionRecord]:
        result = await self.session.execute(select(SessionRecord).order_by(SessionRecord.id))
        return list(result.scalars().all())

    async def get(self, session_id: int) -> SessionRecord | None:
        return await self.session.get(SessionRecord, session_id)

    async def create(self, record: SessionRecord) -> SessionRecord:
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def delete(self, record: SessionRecord) -> None:
        await self.session.delete(record)
        await self.session.commit()

