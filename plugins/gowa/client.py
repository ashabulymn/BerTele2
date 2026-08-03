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
        self.dead_letters: list[dict[str, Any]] = []

    async def send_message(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized_payload = self._normalize_payload(payload)
        if self.config.use_mock_transport:
            return self._mock_send(normalized_payload)

        headers = {"Authorization": f"Bearer {self.config.api_key}"} if self.config.api_key else {}
        url = f"{self.config.api_base_url}/messages"
        self.logger.info(
            "GoWA message send requested",
            extra={
                "recipient": normalized_payload.get("to") or normalized_payload.get("recipient"),
                "message_type": normalized_payload.get("type") or normalized_payload.get("message_type"),
                "timeout_seconds": self.config.timeout_seconds,
            },
        )
        return await self._request_with_retry(url=url, json_payload=normalized_payload, headers=headers)

    def _normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        raw = dict(payload)
        message_type = str(raw.get("type") or raw.get("message_type") or "text").lower()
        if message_type in {"image_url", "photo"}:
            message_type = "image"
        elif message_type in {"voice", "audio_file"}:
            message_type = "audio"
        elif message_type in {"video_file", "video_url"}:
            message_type = "video"
        elif message_type in {"document_file", "file"}:
            message_type = "document"
        elif message_type in {"reply_message", "response", "quoted"}:
            message_type = "reply"
        if message_type not in {"text", "image", "audio", "video", "document", "reply"}:
            message_type = "text"
        normalized = dict(raw)
        normalized["type"] = message_type
        if "message_type" not in normalized and "type" in normalized:
            normalized["message_type"] = message_type
        if "media_url" not in normalized and "file_url" in normalized:
            normalized["media_url"] = normalized["file_url"]
        return normalized

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
                    body = response.json() if response.content else {}
                    self.logger.info(
                        "GoWA message sent",
                        extra={
                            "attempt": attempt,
                            "status_code": response.status_code,
                            "recipient": json_payload.get("to") or json_payload.get("recipient"),
                            "message_type": json_payload.get("type") or json_payload.get("message_type"),
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
                        "recipient": json_payload.get("to") or json_payload.get("recipient"),
                    },
                )
                await asyncio.sleep(delay)

        if last_error is not None:
            self.dead_letters.append(
                {
                    "type": "gowa.send_failure",
                    "payload": json_payload,
                    "error": str(last_error),
                }
            )
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
