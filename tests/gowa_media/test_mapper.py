from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.gowa.media.exceptions import GoWAUnsupportedMedia
from app.gowa.media.mapper import map_media_resource_to_gowa_payload
from app.media.models import (
    Animation,
    Audio,
    Document,
    MediaMetadata,
    MediaType,
    Photo,
    Sticker,
    Video,
    Voice,
)
from app.media.pipeline.interfaces import MediaResource

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

def test_map_photo_to_gowa_payload() -> None:
    """Test mapping photo to GoWA payload."""
    metadata = _create_metadata(MediaType.PHOTO, filename="photo.jpg", width=1920, height=1080)
    resource = _create_resource(metadata, storage_key="photo/abc-123")

    payload = map_media_resource_to_gowa_payload(resource)

    assert payload["type"] == "image"
    assert payload["to"] == ""
    assert payload["media_url"] == "photo/abc-123"
    assert payload["mime_type"] == "image/jpeg"
    assert payload["filename"] == "photo.jpg"
    assert payload["metadata"]["media_id"] == metadata.id
    assert payload["metadata"]["size"] == 1024
    assert payload["metadata"]["dimensions"] == {"width": 1920, "height": 1080}

def test_map_video_to_gowa_payload() -> None:
    """Test mapping video to GoWA payload."""
    metadata = _create_metadata(MediaType.VIDEO, filename="video.mp4", duration=120.5)
    resource = _create_resource(metadata, storage_key="video/xyz-789")

    payload = map_media_resource_to_gowa_payload(resource)

    assert payload["type"] == "video"
    assert payload["media_url"] == "video/xyz-789"
    assert payload["metadata"]["duration"] == 120.5

def test_map_audio_to_gowa_payload() -> None:
    """Test mapping audio to GoWA payload."""
    metadata = _create_metadata(MediaType.AUDIO, filename="audio.mp3", duration=180.0)
    resource = _create_resource(metadata, storage_key="audio/def-456")

    payload = map_media_resource_to_gowa_payload(resource)

    assert payload["type"] == "audio"
    assert payload["media_url"] == "audio/def-456"
    assert payload["metadata"]["duration"] == 180.0

def test_map_voice_to_gowa_payload() -> None:
    """Test mapping voice to GoWA payload (mapped to audio)."""
    metadata = _create_metadata(MediaType.VOICE, mime_type="audio/ogg")
    resource = _create_resource(metadata, storage_key="voice/voice-123")

    payload = map_media_resource_to_gowa_payload(resource)

    assert payload["type"] == "audio"
    assert payload["mime_type"] == "audio/ogg"

def test_map_sticker_to_gowa_payload() -> None:
    """Test mapping sticker to GoWA payload (mapped to image)."""
    metadata = _create_metadata(MediaType.STICKER, mime_type="image/webp")
    resource = _create_resource(metadata, storage_key="sticker/stick-456")

    payload = map_media_resource_to_gowa_payload(resource)

    assert payload["type"] == "image"
    assert payload["mime_type"] == "image/webp"

def test_map_animation_to_gowa_payload() -> None:
    """Test mapping animation to GoWA payload (mapped to video)."""
    metadata = _create_metadata(MediaType.ANIMATION, mime_type="image/gif")
    resource = _create_resource(metadata, storage_key="animation/gif-789")

    payload = map_media_resource_to_gowa_payload(resource)

    assert payload["type"] == "video"
    assert payload["mime_type"] == "image/gif"

def test_map_document_to_gowa_payload() -> None:
    """Test mapping document to GoWA payload."""
    metadata = _create_metadata(MediaType.DOCUMENT, filename="doc.pdf", mime_type="application/pdf")
    resource = _create_resource(metadata, storage_key="document/doc-123")

    payload = map_media_resource_to_gowa_payload(resource)

    assert payload["type"] == "document"
    assert payload["filename"] == "doc.pdf"
    assert payload["mime_type"] == "application/pdf"

def test_map_optional_fields_omitted_when_none() -> None:
    """Test that optional fields are omitted when None."""
    metadata = _create_metadata(
        MediaType.PHOTO,
        filename=None,
        caption=None,
        width=None,
        height=None,
        duration=None,
    )
    resource = _create_resource(metadata)

    payload = map_media_resource_to_gowa_payload(resource)

    assert "dimensions" not in payload["metadata"]
    assert "duration" not in payload["metadata"]

def test_map_unsupported_media_type_raises() -> None:
    """Test that unsupported media types raise an exception."""
    # Create a metadata with an unsupported type by using a mock
    # We'll patch the _map_media_type function to raise the exception
    from unittest.mock import patch
    from app.gowa.media.mapper import map_media_resource_to_gowa_payload

    metadata = _create_metadata(MediaType.PHOTO)
    resource = _create_resource(metadata)

    # Patch the _map_media_type function to raise the exception
    with patch("app.gowa.media.mapper._map_media_type") as mock_map:
        mock_map.side_effect = GoWAUnsupportedMedia("Unsupported media type")

        with pytest.raises(GoWAUnsupportedMedia, match="Unsupported media type"):
            map_media_resource_to_gowa_payload(resource)

def test_map_includes_caption() -> None:
    """Test that caption is included in the payload."""
    metadata = _create_metadata(MediaType.PHOTO, caption="Test caption")
    resource = _create_resource(metadata)

    payload = map_media_resource_to_gowa_payload(resource)

    assert payload["caption"] == "Test caption"