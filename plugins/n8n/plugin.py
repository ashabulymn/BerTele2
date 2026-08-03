from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.events import EventBroker
from app.plugins.base import PluginBase
from app.plugins.manifest import PluginManifest

from .config import N8NConfig
from .mapper import map_outgoing_event_to_payload, map_send_payload_to_event, map_webhook_to_event
from .models import N8NMessageRequest, N8NOutboundEvent, N8NWebhookPayload


class N8NPlugin(PluginBase):
    def __init__(self, *, config: N8NConfig | None = None, logger: logging.Logger | None = None) -> None:
        self.config = config or N8NConfig()
        self.logger = logger or logging.getLogger("plugins.n8n")
        self.dead_letters: list[dict[str, Any]] = []
        self.broker = EventBroker(logger=self.logger)
        manifest = self.build_manifest()
        super().__init__(manifest=manifest, logger=self.logger)
        self.context.broker = self.broker
        self.context.config.update(self.config.model_dump(exclude_none=True))
        self.broker.subscribe(N8NOutboundEvent, self._handle_outgoing_event, name="n8n-outgoing")

    @classmethod
    def build_manifest(cls) -> PluginManifest:
        return PluginManifest(
            plugin_id="n8n",
            name="n8n",
            version="1.0.0",
            entrypoint="plugins.n8n.plugin:N8NPlugin",
            description="Official n8n connector for BerTele2",
            min_app_version="0.1.0",
        )

    async def _handle_outgoing_event(self, event: N8NOutboundEvent) -> None:
        if event.payload.get("metadata", {}).get("skip_transport"):
            return
        try:
            payload = map_outgoing_event_to_payload(event.payload)
            self.logger.info(
                "n8n outgoing event received",
                extra={
                    "workflow_id": payload.get("workflow_id"),
                    "event_name": payload.get("event_name"),
                    "node": payload.get("node"),
                },
            )
            await self._send_to_n8n(payload)
            self.logger.info(
                "n8n outbound delivery succeeded",
                extra={"event_id": event.event_id, "workflow_id": payload.get("workflow_id")},
            )
        except Exception as exc:
            self.dead_letters.append(
                {
                    "event_id": event.event_id,
                    "type": "n8n.outgoing.dead_letter",
                    "payload": event.payload,
                    "error": str(exc),
                    "failed_at": datetime.now(UTC).isoformat(),
                }
            )
            self.logger.exception(
                "n8n outbound delivery failed; dead letter recorded",
                extra={"event_id": event.event_id, "workflow_id": event.payload.get("workflow_id")},
            )

    async def _send_to_n8n(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.config.use_mock_transport:
            self.logger.info(
                "n8n mocked send",
                extra={
                    "workflow_id": payload.get("workflow_id"),
                    "event_name": payload.get("event_name"),
                    "node": payload.get("node"),
                },
            )
            return {
                "status": "accepted",
                "provider": "n8n",
                "mock": True,
                "workflow_id": payload.get("workflow_id"),
                "event_name": payload.get("event_name"),
            }

        target_url = self._webhook_url(payload.get("workflow_id"))
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
        if self.config.bearer_token:
            headers["Authorization"] = f"Bearer {self.config.bearer_token}"
        body = payload.get("payload") or {}
        if "workflow_id" in body:
            body = dict(body)
        return await self._request_with_retry(url=target_url, json_payload=body, headers=headers)

    def _webhook_url(self, workflow_id: str | None) -> str:
        if workflow_id:
            return f"{self.config.api_base_url}{self.config.webhook_path.rstrip('/')}/{workflow_id}"
        return self.config.default_webhook_url

    async def _request_with_retry(self, *, url: str, json_payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.config.max_retries + 2):
            try:
                async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                    response = await client.post(url, json=json_payload, headers=headers)
                    response.raise_for_status()
                    body = response.json() if response.content else {}
                    self.logger.info(
                        "n8n message sent",
                        extra={
                            "attempt": attempt,
                            "status_code": response.status_code,
                            "workflow_id": url.rsplit("/", 1)[-1],
                        },
                    )
                    return body
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt > self.config.max_retries:
                    break
                delay = min(self.config.backoff_factor * (2 ** (attempt - 1)), self.config.max_backoff)
                self.logger.warning(
                    "n8n send failed; retrying",
                    extra={"attempt": attempt, "delay_seconds": delay, "error": str(exc)},
                )
                await asyncio.sleep(delay)

        if last_error is not None:
            self.dead_letters.append({
                "type": "n8n.send_failure",
                "payload": json_payload,
                "error": str(last_error),
            })
            raise RuntimeError(f"n8n send failed after retries: {last_error}") from last_error
        raise RuntimeError("n8n send failed without a retryable error")

    async def publish_event(self, event: Any) -> None:
        self.broker.start()
        await self.broker.publish(event)

    async def handle_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        validated = N8NWebhookPayload.model_validate(payload)
        event = map_webhook_to_event(validated.model_dump(exclude_none=True, by_alias=True))
        await self.publish_event(event)
        self.logger.info(
            "n8n webhook processed",
            extra={"event_name": event.name, "event_id": event.event_id, "workflow_id": event.payload.get("workflow_id")},
        )
        return {
            "status": "accepted",
            "provider": "n8n",
            "event_id": event.event_id,
            "workflow_id": event.payload.get("workflow_id"),
            "event_name": event.payload.get("event"),
        }

    async def handle_send(self, payload: dict[str, Any]) -> dict[str, Any]:
        validated = N8NMessageRequest.model_validate(payload)
        event = map_send_payload_to_event(validated.model_dump(exclude_none=True, by_alias=True))
        await self.publish_event(event)
        self.logger.info(
            "n8n send queued",
            extra={"event_id": event.event_id, "workflow_id": event.payload.get("workflow_id"), "node": event.payload.get("node")},
        )
        return {
            "status": "queued",
            "provider": "n8n",
            "event_id": event.event_id,
            "workflow_id": event.payload.get("workflow_id"),
            "event_name": event.payload.get("event_name"),
        }

    async def status(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "provider": "n8n",
            "enabled": self.config.enabled,
            "base_url": self.config.base_url,
            "ready": self.config.enabled,
            "dead_letter_count": len(self.dead_letters),
        }

    async def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "provider": "n8n",
            "healthy": True,
            "ready": self.config.enabled,
            "dead_letter_count": len(self.dead_letters),
        }

    async def stop(self) -> None:
        await self.broker.stop()
        self.logger.info("n8n connector stopped")
