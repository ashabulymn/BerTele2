from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    apikeys,
    auth,
    dialogs,
    gowa_media,
    health,
    messages,
    meta,
    sessions,
    telegram,
    users,
    webhooks,
)
from app.media.router import router as media_router
from app.telegram.media.router import router as telegram_media_router

router = APIRouter()
router.include_router(auth.router, tags=["auth"])
router.include_router(apikeys.router, tags=["apikeys"])
router.include_router(users.router, tags=["users"])
router.include_router(health.router, tags=["health"])
router.include_router(meta.router, tags=["meta"])
router.include_router(dialogs.router, tags=["dialogs"])
router.include_router(telegram.router, tags=["telegram"])
router.include_router(messages.router, tags=["messages"])
router.include_router(sessions.router, tags=["sessions"])
router.include_router(webhooks.router, tags=["webhooks"])
router.include_router(media_router, tags=["media"])
router.include_router(telegram_media_router, tags=["telegram-media"])
router.include_router(gowa_media.router, tags=["gowa-media"])
