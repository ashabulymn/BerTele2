from __future__ import annotations

import logging
from dataclasses import dataclass

from app.events import Event, EventBroker
from app.integrations.webhook.dispatcher import WebhookDispatcher
from app.integrations.webhook.repository import WebhookRepository


@dataclass
class WebhookManager:
    broker: EventBroker
    repository: WebhookRepository
    dispatcher: WebhookDispatcher
    logger: logging.Logger

    def subscribe(self, event_type: type[Event] = Event) -> None:
        self.broker.subscribe(event_type, self.dispatcher, name="webhook.dispatcher")

    def start(self) -> None:
        self.dispatcher.start()

    async def stop(self) -> None:
        await self.dispatcher.stop()
