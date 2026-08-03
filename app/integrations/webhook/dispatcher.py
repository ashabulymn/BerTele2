from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field

from app.events.event import Event
from app.integrations.webhook.delivery import WebhookDeliveryService
from app.integrations.webhook.models import WebhookEndpoint
from app.integrations.webhook.repository import WebhookRepository


@dataclass
class WebhookDispatcher:
    repository: WebhookRepository
    delivery_service: WebhookDeliveryService
    logger: logging.Logger
    _task: asyncio.Task[None] | None = field(default=None, init=False, repr=False)
    _stopped: asyncio.Event = field(default_factory=asyncio.Event, init=False, repr=False)

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._stopped.clear()
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._stopped.set()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def __call__(self, event: Event) -> None:
        endpoints = await self.repository.list_endpoints()
        for endpoint in endpoints:
            if not endpoint.is_active or not self._matches(endpoint, event):
                continue
            delivery = await self.delivery_service.deliver(endpoint, event.name, {"event_id": event.event_id, "payload": event.payload})
            await self.repository.save_delivery(delivery)

    def _matches(self, endpoint: WebhookEndpoint, event: Event) -> bool:
        if not endpoint.filters:
            return True
        return any(event.name == webhook_filter.event_name for webhook_filter in endpoint.filters)

    async def _run(self) -> None:
        self.logger.debug("Webhook dispatcher background worker started")
        while not self._stopped.is_set():
            await asyncio.sleep(1)
