from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import dialogs, health, messages, meta, sessions, telegram, webhooks

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(meta.router, tags=["meta"])
router.include_router(dialogs.router, tags=["dialogs"])
router.include_router(telegram.router, tags=["telegram"])
router.include_router(messages.router, tags=["messages"])
router.include_router(sessions.router, tags=["sessions"])
router.include_router(webhooks.router, tags=["webhooks"])
