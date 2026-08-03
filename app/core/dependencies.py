from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.telegram_service import TelegramService
from app.session.service import SessionService


def get_telegram_service(request: Request) -> TelegramService:
    return request.app.state.container.telegram_service


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.container.session_factory() as session:
        yield session


def get_session_service(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SessionService:
    return request.app.state.container.session_service(session)
