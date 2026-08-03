from __future__ import annotations

import logging
from typing import Any

from app.events import EventBroker
from app.plugins.base import PluginBase
from app.plugins.manifest import PluginManifest

from .client import GoWAClient
from .config import GoWAConfig
from .mapper import (
    map_outgoing_event_to_message,
    map_outgoing_payload_to_event,
    map_webhook_to_event,
)
from .models import GoWAOutboundEvent


class GoWAPlugin(PluginBase):
    def __init__(self, *, config: GoWAConfig | None = None, logger: logging.Logger | None = None) -> None:
        self.config = config or GoWAConfig()
        self.logger = logger or logging.getLogger("plugins.gowa")
        self.client = GoWAClient(config=self.config, logger=self.logger)
        self.broker = EventBroker(logger=self.logger)
        manifest = self.build_manifest()
        super().__init__(manifest=manifest, logger=self.logger)
        self.context.broker = self.broker
        self.context.config.update(self.config.model_dump(exclude_none=True))
        self.broker.subscribe(GoWAOutboundEvent, self._handle_outgoing_event, name="gowa-outgoing")

    @classmethod
    def build_manifest(cls) -> PluginManifest:
        return PluginManifest(
            plugin_id="gowa",
            name="GoWA",
            version="1.0.0",
            entrypoint="plugins.gowa.plugin:GoWAPlugin",
            description="WhatsApp connector for BerTele2",
            min_app_version="0.1.0",
        )

    async def _handle_outgoing_event(self, event: GoWAOutboundEvent) -> None:
        if event.payload.get("metadata", {}).get("skip_transport"):
            return
        payload = map_outgoing_event_to_message(event.payload)
        self.logger.info(
            "GoWA outgoing event received",
            extra={"recipient": payload.get("to"), "message_type": payload.get("type")},
        )
        await self.client.send_message(payload)

    async def publish_event(self, event: Any) -> None:
        await self.broker.publish(event)

    async def handle_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        event = map_webhook_to_event(payload)
        await self.publish_event(event)
        self.logger.info(
            "GoWA webhook processed",
            extra={"event_name": event.name, "event_id": event.event_id},
        )
        return {"status": "accepted", "event_id": event.event_id, "message_type": event.payload.get("message_type")}

    async def handle_send(self, payload: dict[str, Any]) -> dict[str, Any]:
        event = map_outgoing_payload_to_event(payload)
        metadata = dict(event.payload.get("metadata") or {})
        metadata["skip_transport"] = True
        event.payload["metadata"] = metadata
        await self.publish_event(event)
        result = await self.client.send_message(map_outgoing_event_to_message(event.payload))
        result["status"] = "queued"
        result["provider"] = "gowa"
        return result

    async def status(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "provider": "gowa",
            "enabled": self.config.enabled,
            "base_url": self.config.base_url,
            "ready": True,
        }

    async def stop(self) -> None:
        await self.broker.stop()
        self.logger.info("GoWA connector stopped")
