from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.dashboard.realtime import DashboardRealtimeManager
from app.dashboard.service import DashboardService
from app.security.auth import UserRecord, require_authentication

router = APIRouter()
service = DashboardService()
realtime = DashboardRealtimeManager()


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    current_user: Annotated[UserRecord, Depends(require_authentication)],
) -> dict[str, Any]:
    payload = service.overview()
    await realtime.broadcast({"type": "overview", "payload": payload, "user": current_user.username})
    return payload


@router.get("/dashboard/logs")
async def get_dashboard_logs(
    current_user: Annotated[UserRecord, Depends(require_authentication)],
) -> dict[str, Any]:
    payload = service.logs()
    await realtime.broadcast({"type": "logs", "payload": payload, "user": current_user.username})
    return payload


@router.get("/dashboard/metrics")
async def get_dashboard_metrics(
    current_user: Annotated[UserRecord, Depends(require_authentication)],
) -> dict[str, Any]:
    payload = service.metrics()
    await realtime.broadcast({"type": "metrics", "payload": payload, "user": current_user.username})
    return payload


@router.websocket("/dashboard/ws")
async def dashboard_websocket(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token") or websocket.headers.get("authorization", "")
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1].strip()
    if not token:
        await websocket.close(code=1008)
        return

    security_service = getattr(websocket.app.state, "security_service", None)
    if security_service is None:
        await websocket.close(code=1011)
        return

    try:
        user = security_service.get_user_from_token(token)
    except Exception:
        await websocket.close(code=1008)
        return

    await realtime.connect(websocket)
    await websocket.send_json({"type": "welcome", "user": user.username})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await realtime.disconnect(websocket)
