from __future__ import annotations

import asyncio
from types import TracebackType
from typing import Any, Self

import httpx
import pytest

from plugins.gowa.client import GoWAClient
from plugins.gowa.config import GoWAConfig


def test_gowa_status_endpoint(client) -> None:
    response = client.get("/connectors/gowa/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["provider"] == "gowa"


def test_gowa_webhook_endpoint(client) -> None:
    response = client.post(
        "/connectors/gowa/webhook",
        json={
            "from": "15551234567",
            "to": "15557654321",
            "type": "text",
            "text": "hello from GoWA",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "accepted"
    assert payload["message_type"] == "text"


def test_gowa_send_endpoint(client) -> None:
    response = client.post(
        "/connectors/gowa/send",
        json={
            "to": "15557654321",
            "type": "image",
            "media_url": "https://example.com/image.jpg",
            "caption": "hello",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "queued"
    assert payload["provider"] == "gowa"
    assert payload["message_type"] == "image"


def test_gowa_client_retries_exponential_backoff(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    class FakeResponse:
        status_code = 200

        def json(self) -> dict[str, Any]:
            return {"status": "ok"}

        def raise_for_status(self) -> None:
            return None

    class FakeClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
        ) -> None:
            return None

        async def post(self, url: str, json: dict[str, Any], headers: dict[str, str]) -> FakeResponse:
            calls.append(1)
            if len(calls) < 3:
                raise httpx.HTTPError("temporary failure")
            return FakeResponse()

    async def fake_sleep(delay: float) -> None:
        return None

    monkeypatch.setattr("plugins.gowa.client.httpx.AsyncClient", FakeClient)
    monkeypatch.setattr("plugins.gowa.client.asyncio.sleep", fake_sleep)

    client = GoWAClient(config=GoWAConfig(use_mock_transport=False, max_retries=3, base_url="http://localhost:8080"))
    result = asyncio.run(client.send_message({"to": "123", "type": "text", "text": "hi"}))

    assert result["status"] == "ok"
    assert len(calls) == 3
