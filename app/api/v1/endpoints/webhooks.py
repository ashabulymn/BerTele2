from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.core.dependencies import get_session
from app.integrations.webhook.models import WebhookEndpoint, WebhookEventFilter
from app.integrations.webhook.repository import WebhookRepository
from app.schemas.webhooks import WebhookCreate, WebhookInfo, WebhookListResponse, WebhookUpdate

router = APIRouter()


def _to_info(endpoint: WebhookEndpoint) -> WebhookInfo:
    return WebhookInfo(
        id=endpoint.id,
        name=endpoint.name,
        url=endpoint.url,
        is_active=endpoint.is_active,
        created_at=endpoint.created_at,
        updated_at=endpoint.updated_at,
        event_names=[f.event_name for f in endpoint.filters],
    )


@router.post("/webhooks", response_model=WebhookInfo, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    payload: WebhookCreate,
    session: Annotated[object, Depends(get_session)],
) -> WebhookInfo:
    repository = WebhookRepository(session)
    endpoint = WebhookEndpoint(name=payload.name, url=payload.url, secret=payload.secret, is_active=payload.is_active)
    endpoint.filters = [WebhookEventFilter(event_name=name) for name in payload.event_names]
    saved = await repository.create_endpoint(endpoint)
    return _to_info(saved)


@router.get("/webhooks", response_model=WebhookListResponse)
async def list_webhooks(session: Annotated[object, Depends(get_session)]) -> WebhookListResponse:
    repository = WebhookRepository(session)
    return WebhookListResponse(items=[_to_info(endpoint) for endpoint in await repository.list_endpoints()])


@router.get("/webhooks/{id}", response_model=WebhookInfo)
async def get_webhook(id: int, session: Annotated[object, Depends(get_session)]) -> WebhookInfo:
    repository = WebhookRepository(session)
    endpoint = await repository.get_endpoint(id)
    if endpoint is None:
        raise RuntimeError("Webhook not found")
    return _to_info(endpoint)


@router.put("/webhooks/{id}", response_model=WebhookInfo)
async def update_webhook(id: int, payload: WebhookUpdate, session: Annotated[object, Depends(get_session)]) -> WebhookInfo:
    repository = WebhookRepository(session)
    endpoint = await repository.get_endpoint(id)
    if endpoint is None:
        raise RuntimeError("Webhook not found")
    if payload.name is not None:
        endpoint.name = payload.name
    if payload.url is not None:
        endpoint.url = payload.url
    if payload.secret is not None:
        endpoint.secret = payload.secret
    if payload.is_active is not None:
        endpoint.is_active = payload.is_active
    if payload.event_names is not None:
        endpoint.filters = [WebhookEventFilter(event_name=name) for name in payload.event_names]
    await repository.session.commit()
    await repository.session.refresh(endpoint)
    return _to_info(endpoint)


@router.delete("/webhooks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(id: int, session: Annotated[object, Depends(get_session)]) -> Response:
    repository = WebhookRepository(session)
    endpoint = await repository.get_endpoint(id)
    if endpoint is None:
        raise RuntimeError("Webhook not found")
    await repository.session.delete(endpoint)
    await repository.session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
