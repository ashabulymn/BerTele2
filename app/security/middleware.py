from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.authorization = request.headers.get("authorization")
        request.state.api_key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
        request.state.user = None
        response = await call_next(request)
        return response
