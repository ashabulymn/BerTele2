from __future__ import annotations

import asyncio
from typing import Any

from fastapi import WebSocket


class DashboardRealtimeManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        for websocket in list(self._connections):
            try:
                await websocket.send_json(payload)
            except Exception:
                self._connections.discard(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def heartbeat(self, websocket: WebSocket) -> None:
        while True:
            await asyncio.sleep(15)
            try:
                await websocket.send_json({"type": "heartbeat", "timestamp": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat()})
            except Exception:
                break
