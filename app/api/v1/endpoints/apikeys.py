from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict

from app.core.dependencies import get_security_service
from app.security.auth import SecurityService, UserRecord, require_permissions

router = APIRouter(prefix="/apikeys")


class APIKeyCreateRequest(BaseModel):
    name: str
    expires_in_days: int | None = None


class APIKeyPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    prefix: str
    user_id: int
    created_at: str | None = None
    expires_at: str | None = None
    last_used_at: str | None = None
    is_active: bool = True


class APIKeyCreateResponse(BaseModel):
    id: int
    name: str
    prefix: str
    user_id: int
    key: str
    created_at: str | None = None
    expires_at: str | None = None
    is_active: bool = True


@router.post("", response_model=APIKeyCreateResponse, dependencies=[Depends(require_permissions("apikeys:write"))])
async def create_api_key(
    payload: APIKeyCreateRequest,
    current_user: Annotated[UserRecord, Depends(require_permissions("apikeys:write"))],
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> APIKeyCreateResponse:
    data = security_service.create_api_key(current_user.id, payload.name, expires_in_days=payload.expires_in_days)
    return APIKeyCreateResponse(**data)


@router.get("", response_model=list[APIKeyPublic], dependencies=[Depends(require_permissions("apikeys:read"))])
async def list_api_keys(
    current_user: Annotated[UserRecord, Depends(require_permissions("apikeys:read"))],
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> list[APIKeyPublic]:
    records = security_service.list_api_keys(current_user.id)
    return [APIKeyPublic(**record) for record in records]


@router.delete("/{id}", dependencies=[Depends(require_permissions("apikeys:write"))])
async def delete_api_key(
    id: Annotated[int, Path(title="API key identifier")],
    current_user: Annotated[UserRecord, Depends(require_permissions("apikeys:write"))],
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> dict[str, str]:
    records = security_service.list_api_keys(current_user.id)
    api_key_ids = {record["id"] for record in records}
    if id not in api_key_ids:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="API key not found")
    if not security_service.revoke_api_key(id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="API key not found")
    return {"status": "deleted", "id": str(id)}
