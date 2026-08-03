from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict

from app.core.dependencies import get_security_service
from app.security.auth import SecurityService, UserRecord, require_permissions

router = APIRouter(prefix="/users")


class UserCreateRequest(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    password: str
    roles: list[str] | None = None


class UserUpdateRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    password: str | None = None
    roles: list[str] | None = None
    is_active: bool | None = None


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    roles: list[str]
    is_active: bool = True
    is_superuser: bool = False


@router.get("", response_model=list[UserPublic], dependencies=[Depends(require_permissions("users:read"))])
async def list_users(
    current_user: Annotated[UserRecord, Depends(require_permissions("users:read"))],
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> list[UserPublic]:
    return [UserPublic.model_validate(user.to_public_dict()) for user in security_service.list_users()]


@router.post("", response_model=UserPublic, dependencies=[Depends(require_permissions("users:write"))])
async def create_user(
    payload: UserCreateRequest,
    current_user: Annotated[UserRecord, Depends(require_permissions("users:write"))],
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> UserPublic:
    try:
        user = security_service.create_user(
            username=payload.username,
            password=payload.password,
            email=payload.email,
            full_name=payload.full_name,
            roles=payload.roles,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return UserPublic.model_validate(user.to_public_dict())


@router.put("/{id}", response_model=UserPublic, dependencies=[Depends(require_permissions("users:write"))])
async def update_user(
    id: Annotated[int, Path(title="User identifier")],
    payload: UserUpdateRequest,
    current_user: Annotated[UserRecord, Depends(require_permissions("users:write"))],
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> UserPublic:
    try:
        user = security_service.update_user(
            id,
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
            roles=payload.roles,
            is_active=payload.is_active,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return UserPublic.model_validate(user.to_public_dict())
