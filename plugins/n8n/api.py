from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from .webhook import connector, require_n8n_auth

router = APIRouter(prefix="/connectors/n8n", tags=["n8n"])


@router.post("/send", dependencies=[Depends(require_n8n_auth)])
async def send_message(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if payload is None:
        raise HTTPException(status_code=400, detail="n8n payload is required")
    try:
        return await connector.handle_send(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
