from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.core.dependencies import get_session_service
from app.schemas.sessions import SessionCreate, SessionInfo, SessionListResponse
from app.session.service import SessionService

router = APIRouter()


@router.post("/sessions", response_model=SessionInfo, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SessionCreate,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionInfo:
    return await service.create_session(**payload.model_dump())


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(service: Annotated[SessionService, Depends(get_session_service)]) -> SessionListResponse:
    return SessionListResponse(items=await service.list_sessions())


@router.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session(
    session_id: int,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionInfo:
    return await service.get_session(session_id)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> Response:
    await service.delete_session(session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/sessions/{session_id}/connect", response_model=SessionInfo)
async def connect_session(
    session_id: int,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionInfo:
    return await service.connect(session_id)


@router.post("/sessions/{session_id}/disconnect", response_model=SessionInfo)
async def disconnect_session(
    session_id: int,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionInfo:
    return await service.disconnect(session_id)


@router.post("/sessions/{session_id}/reconnect", response_model=SessionInfo)
async def reconnect_session(
    session_id: int,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionInfo:
    return await service.reconnect(session_id)

