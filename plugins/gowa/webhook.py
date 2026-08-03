from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from .plugin import GoWAPlugin

router = APIRouter(prefix="/connectors/gowa", tags=["gowa"])
connector = GoWAPlugin()


@router.post("/webhook")
async def receive_webhook(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    return await connector.handle_webhook(payload)


@router.get("/status")
async def get_status() -> dict[str, Any]:
    return await connector.status()


@router.post("/send")
async def send_message(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if payload is None:
        raise HTTPException(status_code=400, detail="GoWA payload is required")
    return await connector.handle_send(payload)
