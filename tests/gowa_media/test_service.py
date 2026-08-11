from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.gowa.media.exceptions import GoWAMediaSendError, GoWAUnsupportedMedia, GoWAValidationError
from app.gowa.media.sender import GoWAMediaSender
from app.gowa.media.service import GoWAMediaService
from app.media.models import MediaMetadata, MediaType
from app.media.pipeline.interfaces import MediaResource
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
async def test_service_send_media_success() -> None:
    """Test successful media sending through service."""
    metadata = _create_metadata(MediaType.PHOTO)
    resource = _create_resource(metadata)

    mock_sender = AsyncMock(spec=GoWAMediaSender)
    mock_sender.send.return_value = {
        "status": "sent",
        "media_id": metadata.id,
        "device_id": "dev-001",
        "chat_id": "15551234567",
        "message_id": "gowa-image-12345",
        "provider": "gowa",
    }

    config = GoWAConfig(enabled=True, use_mock_transport=True)
    service = GoWAMediaService(config=config, sender=mock_sender)

    result = await service.send_media(resource, device_id="dev-001", chat_id="15551234567")

    assert result["status"] == "sent"
    assert result["media_id"] == metadata.id
    assert result["device_id"] == "dev-001"
    assert result["chat_id"] == "15551234567"
    mock_sender.send.assert_called_once_with(resource, "dev-001", "15551234567")


@pytest.mark.anyio
async def test_service_validation_error_propagates() -> None:
    """Test that validation errors propagate from sender."""
    metadata = _create_metadata(MediaType.PHOTO)
    resource = _create_resource(metadata)

    mock_sender = AsyncMock(spec=GoWAMediaSender)
    mock_sender.send.side_effect = GoWAValidationError("Invalid resource")

    config = GoWAConfig(enabled=True, use_mock_transport=True)
    service = GoWAMediaService(config=config, sender=mock_sender)

    with pytest.raises(GoWAValidationError, match="Invalid resource"):
        await service.send_media(resource, device_id="dev-001", chat_id="15551234567")


@pytest.mark.anyio
async def test_service_unsupported_media_propagates() -> None:
    """Test that unsupported media errors propagate from sender."""
    metadata = _create_metadata(MediaType.PHOTO)
    resource = _create_resource(metadata)

    mock_sender = AsyncMock(spec=GoWAMediaSender)
    mock_sender.send.side_effect = GoWAUnsupportedMedia("Unsupported type")

    config = GoWAConfig(enabled=True, use_mock_transport=True)
    service = GoWAMediaService(config=config, sender=mock_sender)

    with pytest.raises(GoWAUnsupportedMedia, match="Unsupported type"):
        await service.send_media(resource, device_id="dev-001", chat_id="15551234567")


@pytest.mark.anyio
async def test_service_send_error_propagates() -> None:
    """Test that send errors propagate from sender."""
    metadata = _create_metadata(MediaType.PHOTO)
    resource = _create_resource(metadata)

    mock_sender = AsyncMock(spec=GoWAMediaSender)
    mock_sender.send.side_effect = GoWAMediaSendError("Send failed")

    config = GoWAConfig(enabled=True, use_mock_transport=True)
    service = GoWAMediaService(config=config, sender=mock_sender)

    with pytest.raises(GoWAMediaSendError, match="Send failed"):
        await service.send_media(resource, device_id="dev-001", chat_id="15551234567")


@pytest.mark.anyio
async def test_service_unexpected_error_wrapped() -> None:
    """Test that unexpected errors are wrapped in GoWAMediaSendError."""
    metadata = _create_metadata(MediaType.PHOTO)
    resource = _create_resource(metadata)

    mock_sender = AsyncMock(spec=GoWAMediaSender)
    mock_sender.send.side_effect = RuntimeError("Unexpected error")

    config = GoWAConfig(enabled=True, use_mock_transport=True)
    service = GoWAMediaService(config=config, sender=mock_sender)

    with pytest.raises(GoWAMediaSendError, match="Unexpected error sending media"):
        await service.send_media(resource, device_id="dev-001", chat_id="15551234567")


def test_service_configuration_validation_disabled() -> None:
    """Test service validation when GoWA is disabled."""
    config = GoWAConfig(enabled=False, use_mock_transport=True)
    service = GoWAMediaService(config=config)

    with pytest.raises(GoWAValidationError, match="not enabled"):
        # We need to call a method that validates config
        # Since send_media is async, we'll test the validation directly
        service._validate_configuration()


def test_service_configuration_validation_no_base_url() -> None:
    """Test service validation when base_url is missing."""
    config = GoWAConfig(enabled=True, base_url="", use_mock_transport=True)
    service = GoWAMediaService(config=config)

    with pytest.raises(GoWAValidationError, match="base_url"):
        service._validate_configuration()


def test_service_initialization() -> None:
    """Test service initialization with custom dependencies."""
    config = GoWAConfig(use_mock_transport=True)
    mock_sender = AsyncMock(spec=GoWAMediaSender)
    
    service = GoWAMediaService(config=config, sender=mock_sender)
    
    assert service.config is config
    assert service.sender is mock_sender


def test_service_creates_default_sender() -> None:
    """Test that service creates default sender when not provided."""
    config = GoWAConfig(use_mock_transport=True)
    service = GoWAMediaService(config=config)
    
    assert service.sender is not None
    assert isinstance(service.sender, GoWAMediaSender)