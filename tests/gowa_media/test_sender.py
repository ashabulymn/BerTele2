from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.gowa.media.exceptions import GoWAMediaSendError, GoWAUnsupportedMedia, GoWAValidationError
from app.gowa.media.mapper import map_media_resource_to_gowa_payload
from app.gowa.media.sender import GoWAMediaSender
from app.media.models import MediaMetadata, MediaType
from app.media.pipeline.interfaces import MediaResource
from plugins.gowa.client import GoWAClient
from plugins.gowa.config import GoWAConfig


def _create_metadata(media_type: MediaType, **kwargs: object) -> MediaMetadata:
    """Helper to create media metadata for testing."""
    defaults = {
        "type": media_type,
        "mime_type": "image/jpeg",
        "size": 1024,
        "sha256": "abc123",
        "created_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    return MediaMetadata(**defaults)


def _create_resource(metadata: MediaMetadata, storage_key: str = "test/key") -> MediaResource:
    """Helper to create a MediaResource for testing."""
    return MediaResource(metadata=metadata, storage_key=storage_key, content=b"test", ready=True)


@pytest.mark.anyio
async def test_sender_success() -> None:
    """Test successful media sending."""
    metadata = _create_metadata(MediaType.PHOTO, filename="photo.jpg")
    resource = _create_resource(metadata, storage_key="photo/abc-123")

    mock_client = AsyncMock(spec=GoWAClient)
    mock_client.send_message.return_value = {
        "status": "accepted",
        "provider": "gowa",
        "message_id": "gowa-image-12345",
    }

    sender = GoWAMediaSender(gowa_client=mock_client)
    result = await sender.send(resource, recipient="15551234567")

    assert result["status"] == "sent"
    assert result["media_id"] == metadata.id
    assert result["recipient"] == "15551234567"
    assert result["message_id"] == "gowa-image-12345"
    assert result["provider"] == "gowa"

    # Verify the payload sent to GoWA client
    call_args = mock_client.send_message.call_args
    payload = call_args[0][0] if call_args[0] else call_args[1]["payload"]
    assert payload["to"] == "15551234567"
    assert payload["type"] == "image"
    assert payload["media_url"] == "photo/abc-123"


@pytest.mark.anyio
async def test_sender_validation_error() -> None:
    """Test sender validation errors."""
    # Missing storage_key
    resource = MediaResource(
        metadata=_create_metadata(MediaType.PHOTO),
        storage_key="",
        content=b"test",
        ready=True,
    )

    sender = GoWAMediaSender()
    with pytest.raises(GoWAValidationError, match="storage_key"):
        await sender.send(resource, recipient="15551234567")

    # Not ready
    resource = MediaResource(
        metadata=_create_metadata(MediaType.PHOTO),
        storage_key="photo/abc-123",
        content=b"test",
        ready=False,
    )

    with pytest.raises(GoWAValidationError, match="not ready"):
        await sender.send(resource, recipient="15551234567")

    # Missing mime_type
    metadata = _create_metadata(MediaType.PHOTO)
    metadata.mime_type = ""  # type: ignore[assignment]
    resource = MediaResource(
        metadata=metadata,
        storage_key="photo/abc-123",
        content=b"test",
        ready=True,
    )

    with pytest.raises(GoWAValidationError, match="mime_type"):
        await sender.send(resource, recipient="15551234567")


@pytest.mark.anyio
async def test_sender_unsupported_media_type() -> None:
    """Test sender with unsupported media type."""
    from unittest.mock import patch

    metadata = _create_metadata(MediaType.PHOTO)
    resource = _create_resource(metadata)

    sender = GoWAMediaSender()

    # Patch the map_media_resource_to_gowa_payload function to raise the exception
    with patch("app.gowa.media.sender.map_media_resource_to_gowa_payload") as mock_map:
        mock_map.side_effect = GoWAUnsupportedMedia("Unsupported media type")

        with pytest.raises(GoWAUnsupportedMedia, match="Unsupported media type"):
            await sender.send(resource, recipient="15551234567")


@pytest.mark.anyio
async def test_sender_failure_raises_media_send_error() -> None:
    """Test that sender failures raise GoWAMediaSendError."""
    metadata = _create_metadata(MediaType.PHOTO)
    resource = _create_resource(metadata)

    mock_client = AsyncMock(spec=GoWAClient)
    mock_client.send_message.side_effect = RuntimeError("Network error")

    sender = GoWAMediaSender(gowa_client=mock_client)
    with pytest.raises(GoWAMediaSendError, match="Failed to send media"):
        await sender.send(resource, recipient="15551234567")


@pytest.mark.anyio
async def test_sender_uses_default_client() -> None:
    """Test that sender creates default client when not provided."""
    config = GoWAConfig(use_mock_transport=True)
    sender = GoWAMediaSender(config=config)
    
    assert sender.gowa_client is not None
    assert isinstance(sender.gowa_client, GoWAClient)


def test_sender_initialization() -> None:
    """Test sender initialization with custom dependencies."""
    config = GoWAConfig(use_mock_transport=True)
    mock_client = AsyncMock(spec=GoWAClient)
    
    sender = GoWAMediaSender(gowa_client=mock_client, config=config)
    
    assert sender.gowa_client is mock_client
    assert sender.config is config