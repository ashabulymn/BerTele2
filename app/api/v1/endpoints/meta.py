from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.version import VersionResponse

router = APIRouter()


@router.get("/version", response_model=VersionResponse)
async def version() -> VersionResponse:
    settings = get_settings()
    return VersionResponse(version=settings.version, app_name=settings.app_name)
