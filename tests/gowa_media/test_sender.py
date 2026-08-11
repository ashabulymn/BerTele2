from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.gowa.media.exceptions import GoWAMediaSendError, GoWAUnsupportedMedia, GoWAValidationError
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


def _create_resource(
    metadata: MediaMetadata | None = None,
    storage_key: str = "test/key",
    *,
    content: bytes | None = b"test",
    ready: bool = True,
) -> MediaResource:
    """Helper to create a MediaResource for testing."""
    return MediaResource(
        metadata=metadata or _create_metadata(MediaType.PHOTO),
        storage_key=storage_key,
        content=content,
        ready=ready,
    )


@pytest.mark.anyio
async def test_sender_success() -> None:
    """Test successful media sending with device_id and chat_id."""
    metadata = _create_metadata(MediaType.PHOTO, filename="photo.jpg")
    resource = _create_resource(metadata, storage_key="photo/abc-123")

    mock_client = AsyncMock(spec=GoWAClient)
    mock_client.send_message.return_value = {
        "status": "accepted",
        "provider": "gowa",
        "message_id": "gowa-image-12345",
    }

    sender = GoWAMediaSender(gowa_client=mock_client)
    result = await sender.send(resource, device_id="dev-001", chat_id="15551234567")

    assert result["status"] == "sent"
    assert result["media_id"] == metadata.id
    assert result["device_id"] == "dev-001"
    assert result["chat_id"] == "15551234567"
    assert result["message_id"] == "gowa-image-12345"
    assert result["provider"] == "gowa"
    assert result["metadata"]["message_id"] == "gowa-image-12345"


@pytest.mark.anyio
async def test_device_id_propagated_to_payload() -> None:
    """Test that device_id is propagated into the GoWA payload metadata."""
    resource = _create_resource()

    mock_client = AsyncMock(spec=GoWAClient)
    mock_client.send_message.return_value = {"message_id": "gowa-1", "status": "accepted"}

    sender = GoWAMediaSender(gowa_client=mock_client)
    await sender.send(resource, device_id="dev-001", chat_id="15551234567")

    payload = mock_client.send_message.call_args.args[0]
    assert payload["metadata"]["device_id"] == "dev-001"


@pytest.mark.anyio
async def test_chat_id_propagated_to_payload() -> None:
    """Test that chat_id is propagated as the GoWA recipient (to field)."""
    resource = _create_resource()

    mock_client = AsyncMock(spec=GoWAClient)
    mock_client.send_message.return_value = {"message_id": "gowa-1", "status": "accepted"}

    sender = GoWAMediaSender(gowa_client=mock_client)
    await sender.send(resource, device_id="dev-001", chat_id="15551234567")

    payload = mock_client.send_message.call_args.args[0]
    assert payload["to"] == "15551234567"


@pytest.mark.anyio
async def test_media_resource_passed_correctly() -> None:
    """Test that the MediaResource contents are mapped into the payload."""
    metadata = _create_metadata(MediaType.PHOTO, filename="photo.jpg", caption="hello")
    resource = _create_resource(metadata, storage_key="photo/abc-123")

    mock_client = AsyncMock(spec=GoWAClient)
    mock_client.send_message.return_value = {"message_id": "gowa-1", "status": "accepted"}

    sender = GoWAMediaSender(gowa_client=mock_client)
    await sender.send(resource, device_id="dev-001", chat_id="15551234567")

    payload = mock_client.send_message.call_args.args[0]
    assert payload["type"] == "image"
    assert payload["media_url"] == "photo/abc-123"
    assert payload["mime_type"] == "image/jpeg"
    assert payload["filename"] == "photo.jpg"
    assert payload["caption"] == "hello"
    assert payload["metadata"]["media_id"] == metadata.id


@pytest.mark.anyio
async def test_credentials_not_accepted_as_parameters() -> None:
    """Test that credentials are never part of the sender interface.

    The sender accepts only device_id, chat_id and a MediaResource.
    Username/password/host/api_key are not constructor or method params,
    so they cannot be passed as workflow/node fields.
    """
    sender = GoWAMediaSender()
    signature_params = list(GoWAMediaSender.send.__annotations__.keys())
    assert "device_id" in signature_params
    assert "chat_id" in signature_params
    assert "username" not in signature_params
    assert "password" not in signature_params
    assert "host" not in signature_params
    assert "api_key" not in signature_params

    # The sender does not construct authenticated clients from node fields.
    assert sender.config == GoWAConfig(enabled=True, use_mock_transport=True)


@pytest.mark.anyio
async def test_missing_device_id_fails() -> None:
    """Test that sending without device_id raises a validation error."""
    resource = _create_resource()
    sender = GoWAMediaSender(gowa_client=AsyncMock(spec=GoWAClient))

    with pytest.raises(GoWAValidationError, match="device_id"):
        await sender.send(resource, device_id="", chat_id="15551234567")

    with pytest.raises(GoWAValidationError, match="device_id"):
        await sender.send(resource, device_id=None, chat_id="15551234567")


@pytest.mark.anyio
async def test_missing_chat_id_fails() -> None:
    """Test that sending without chat_id raises a validation error."""
    resource = _create_resource()
    sender = GoWAMediaSender(gowa_client=AsyncMock(spec=GoWAClient))

    with pytest.raises(GoWAValidationError, match="chat_id"):
        await sender.send(resource, device_id="dev-001", chat_id="")

    with pytest.raises(GoWAValidationError, match="chat_id"):
        await sender.send(resource, device_id="dev-001", chat_id="   ")


@pytest.mark.anyio
async def test_invalid_media_resource_fails() -> None:
    """Test that invalid media resources raise validation errors."""
    sender = GoWAMediaSender(gowa_client=AsyncMock(spec=GoWAClient))

    # Missing storage_key
    resource = _create_resource(storage_key="")
    with pytest.raises(GoWAValidationError, match="storage_key"):
        await sender.send(resource, device_id="dev-001", chat_id="15551234567")

    # Missing content
    resource = _create_resource(content=None)
    with pytest.raises(GoWAValidationError, match="content"):
        await sender.send(resource, device_id="dev-001", chat_id="15551234567")

    # Not ready
    resource = _create_resource(ready=False)
    with pytest.raises(GoWAValidationError, match="ready"):
        await sender.send(resource, device_id="dev-001", chat_id="15551234567")

    # Missing mime_type
    metadata = _create_metadata(MediaType.PHOTO)
    metadata.mime_type = ""  # type: ignore[assignment]
    resource = _create_resource(metadata)
    with pytest.raises(GoWAValidationError, match="mime_type"):
        await sender.send(resource, device_id="dev-001", chat_id="15551234567")


@pytest.mark.anyio
async def test_unsupported_media_type_raises() -> None:
    """Test that unsupported media types raise GoWAUnsupportedMedia."""
    metadata = _create_metadata(MediaType.PHOTO)
    resource = _create_resource(metadata)

    sender = GoWAMediaSender(gowa_client=AsyncMock(spec=GoWAClient))

    with patch("app.gowa.media.sender.map_media_resource_to_gowa_payload") as mock_map:
        mock_map.side_effect = GoWAUnsupportedMedia("Unsupported media type: text")
        with pytest.raises(GoWAUnsupportedMedia, match="Unsupported media type"):
            await sender.send(resource, device_id="dev-001", chat_id="15551234567")


@pytest.mark.anyio
async def test_authentication_failure_handled() -> None:
    """Test that GoWA authentication failures become GoWAMediaSendError."""
    resource = _create_resource()

    mock_client = AsyncMock(spec=GoWAClient)
    mock_client.send_message.side_effect = RuntimeError("GoWA authentication failed: invalid credentials")

    sender = GoWAMediaSender(gowa_client=mock_client)
    with pytest.raises(GoWAMediaSendError, match="Failed to send media"):
        await sender.send(resource, device_id="dev-001", chat_id="15551234567")


@pytest.mark.anyio
async def test_http_failure_handled() -> None:
    """Test that GoWA HTTP failures become GoWAMediaSendError."""
    resource = _create_resource()

    mock_client = AsyncMock(spec=GoWAClient)
    mock_client.send_message.side_effect = RuntimeError("HTTP 500: Internal Server Error")

    sender = GoWAMediaSender(gowa_client=mock_client)
    with pytest.raises(GoWAMediaSendError, match="Failed to send media"):
        await sender.send(resource, device_id="dev-001", chat_id="15551234567")


@pytest.mark.anyio
async def test_sensitive_credentials_not_exposed_in_errors() -> None:
    """Test that credentials are redacted from sender errors."""
    resource = _create_resource()

    mock_client = AsyncMock(spec=GoWAClient)
    mock_client.send_message.side_effect = RuntimeError(
        "Authorization: Bearer super-secret-token-12345 returned 401"
    )

    sender = GoWAMediaSender(gowa_client=mock_client)
    with pytest.raises(GoWAMediaSendError) as exc_info:
        await sender.send(resource, device_id="dev-001", chat_id="15551234567")

    assert "super-secret-token-12345" not in str(exc_info.value)
    assert "Bearer" not in str(exc_info.value)


@pytest.mark.anyio
async def test_sensitive_credentials_not_logged() -> None:
    """Test that log records never include credential values."""
    resource = _create_resource()
    mock_logger = Mock()
    sender = GoWAMediaSender(gowa_client=AsyncMock(spec=GoWAClient), logger=mock_logger)

    await sender.send(resource, device_id="dev-001", chat_id="15551234567")

    for call in mock_logger.info.call_args_list:
        extra = call.kwargs.get("extra", {})
        for value in extra.values():
            assert "Bearer" not in str(value)
            assert "supersecret" not in str(value)


def test_sender_uses_default_client() -> None:
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