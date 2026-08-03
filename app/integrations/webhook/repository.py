from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.webhook.models import WebhookDeliveryRecord, WebhookEndpoint


class WebhookRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_endpoints(self) -> list[WebhookEndpoint]:
        result = await self.session.execute(select(WebhookEndpoint).order_by(WebhookEndpoint.id))
        return list(result.scalars().unique().all())

    async def get_endpoint(self, endpoint_id: int) -> WebhookEndpoint | None:
        return await self.session.get(WebhookEndpoint, endpoint_id)

    async def create_endpoint(self, endpoint: WebhookEndpoint) -> WebhookEndpoint:
        self.session.add(endpoint)
        await self.session.commit()
        await self.session.refresh(endpoint)
        return endpoint

    async def save_delivery(self, delivery: WebhookDeliveryRecord) -> WebhookDeliveryRecord:
        self.session.add(delivery)
        await self.session.commit()
        await self.session.refresh(delivery)
        return delivery
