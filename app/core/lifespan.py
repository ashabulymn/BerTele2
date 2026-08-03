from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.container import AppContainer


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    container = AppContainer()
    await container.start()
    app.state.container = container
    try:
        yield
    finally:
        await container.stop()

