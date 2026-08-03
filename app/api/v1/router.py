from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import health, messages, meta, telegram

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(meta.router, tags=["meta"])
router.include_router(telegram.router, tags=["telegram"])
router.include_router(messages.router, tags=["messages"])
