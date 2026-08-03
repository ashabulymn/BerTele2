from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from .config import GoWAConfig


class GoWAClient:
    def __init__(self, *, config: GoWAConfig | None = None, logger: logging.Logger | None = None) -> None:
        self.config = config or GoWAConfig()
        self.logger = logger or logging.getLogger("plugins.gowa.client")

    async def send_message(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.config.use_mock_transport:
            return self._mock_send(payload)

        headers = {"Authorization": f"Bearer {self.config.api_key}"} if self.config.api_key else {}
        url = f"{self.config.api_base_url}/messages"
        return await self._request_with_retry(url=url, json_payload=payload, headers=headers)

    async def _request_with_retry(
        self,
        *,
        url: str,
        json_payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.config.max_retries + 2):
            try:
                async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                    response = await client.post(url, json=json_payload, headers=headers)
                    response.raise_for_status()
                    body = response.json()
                    self.logger.info(
                        "GoWA message sent",
                        extra={
                            "attempt": attempt,
                            "status_code": response.status_code,
                            "to": json_payload.get("to"),
                        },
                    )
                    return body
            except httpx.HTTPError as exc:  # pragma: no cover - exercised through retry tests
                last_error = exc
                if attempt > self.config.max_retries:
                    break
                delay = min(self.config.backoff_factor * (2 ** (attempt - 1)), self.config.max_backoff)
                self.logger.warning(
                    "GoWA send failed; retrying",
                    extra={
                        "attempt": attempt,
                        "delay_seconds": delay,
                        "error": str(exc),
                    },
                )
                await asyncio.sleep(delay)

        if last_error is not None:
            raise RuntimeError(f"GoWA send failed after retries: {last_error}") from last_error
        raise RuntimeError("GoWA send failed without a retryable error")

    def _mock_send(self, payload: dict[str, Any]) -> dict[str, Any]:
        message_type = payload.get("type") or payload.get("message_type") or "text"
        self.logger.info(
            "GoWA mocked send",
            extra={
                "recipient": payload.get("to") or payload.get("recipient"),
                "message_type": message_type,
            },
        )
        return {
            "status": "accepted",
            "provider": "gowa",
            "mock": True,
            "message_type": message_type,
            "recipient": payload.get("to") or payload.get("recipient"),
            "message_id": f"gowa-{message_type}-{abs(hash(str(payload))) % 100000}",
        }
