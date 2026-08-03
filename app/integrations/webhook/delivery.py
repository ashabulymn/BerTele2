from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from app.integrations.webhook.models import WebhookDeliveryRecord, WebhookEndpoint
from app.integrations.webhook.retry import WebhookRetryPolicy
from app.integrations.webhook.signer import WebhookSigner


@dataclass
class WebhookDeliveryService:
    logger: logging.Logger
    signer: WebhookSigner
    retry_policy: WebhookRetryPolicy

    async def deliver(self, endpoint: WebhookEndpoint, event_name: str, payload: dict[str, object]) -> WebhookDeliveryRecord:
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        signature = self.signer.sign(endpoint.secret, body)
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event_name,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint.url, content=body, headers=headers)

        status = "delivered" if response.is_success else "failed"
        return WebhookDeliveryRecord(
            endpoint_id=endpoint.id,
            event_name=event_name,
            event_id=str(payload.get("event_id", "")),
            status=status,
            request_headers=json.dumps(headers),
            request_body=body.decode("utf-8"),
            response_status=response.status_code,
            response_body=response.text,
            attempt_count=1,
            delivered_at=datetime.now(UTC) if response.is_success else None,
        )
