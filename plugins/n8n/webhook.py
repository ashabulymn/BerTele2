from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from .plugin import N8NPlugin

router = APIRouter(prefix="/connectors/n8n", tags=["n8n"])
connector = N8NPlugin()


def _validate_credentials(x_api_key: str | None, authorization: str | None) -> None:
    if not connector.config.api_key and not connector.config.bearer_token:
        return
    if x_api_key and connector.config.api_key and x_api_key == connector.config.api_key:
        return
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
        if connector.config.bearer_token and token == connector.config.bearer_token:
            return
    raise HTTPException(status_code=401, detail="Invalid or missing n8n authentication")


async def require_n8n_auth(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="x-api-key"),
    authorization: str | None = Header(default=None),
) -> None:
    del request
    _validate_credentials(x_api_key, authorization)


@router.post("/events", dependencies=[Depends(require_n8n_auth)])
async def receive_event(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if payload is None:
        raise HTTPException(status_code=400, detail="n8n payload is required")
    try:
        return await connector.handle_event(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/status")
async def get_status() -> dict[str, Any]:
    return await connector.status()


@router.get("/health")
async def get_health() -> dict[str, Any]:
    return await connector.health()
