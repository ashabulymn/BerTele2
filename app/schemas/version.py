from __future__ import annotations

from app.schemas.common import APIModel


class VersionResponse(APIModel):
    version: str
    app_name: str

