from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from .plugin import GoWAPlugin

router = APIRouter(prefix="/connectors/gowa", tags=["gowa"])
connector = GoWAPlugin()


@router.post("/webhook")
async def receive_webhook(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if payload is None:
        raise HTTPException(status_code=400, detail="GoWA payload is required")
    try:
        return await connector.handle_webhook(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/status")
async def get_status() -> dict[str, Any]:
    return await connector.status()


@router.get("/health")
async def get_health() -> dict[str, Any]:
    return await connector.health()


@router.post("/send")
async def send_message(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if payload is None:
        raise HTTPException(status_code=400, detail="GoWA payload is required")
    try:
        return await connector.handle_send(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
