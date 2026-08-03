from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from app.core.dependencies import get_security_service
from app.security.auth import SecurityService, UserRecord, require_authentication

router = APIRouter(prefix="/auth")


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    roles: list[str]
    is_active: bool = True
    is_superuser: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserPublic


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> TokenResponse:
    try:
        user = security_service.authenticate_user(payload.username, payload.password)
    except Exception as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password") from exc
    access_token, refresh_token = security_service.issue_tokens(user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserPublic.model_validate(user.to_public_dict()),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    security_service: Annotated[SecurityService, Depends(get_security_service)],
) -> TokenResponse:
    token = payload.refresh_token
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Refresh token is required")
    try:
        user = security_service.get_user_from_refresh_token(token)
    except Exception as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc
    access_token, refresh_token = security_service.issue_tokens(user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserPublic.model_validate(user.to_public_dict()),
    )


@router.post("/logout")
async def logout(
    current_user: Annotated[UserRecord, Depends(require_authentication)],
) -> dict[str, str]:
    return {"status": "ok", "message": f"Logged out user {current_user.username}"}


@router.get("/me", response_model=UserPublic)
async def me(
    current_user: Annotated[UserRecord, Depends(require_authentication)],
) -> UserPublic:
    return UserPublic.model_validate(current_user.to_public_dict())
