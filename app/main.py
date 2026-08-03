from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.lifespan import lifespan

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)
app.include_router(v1_router, prefix=settings.api_prefix)

