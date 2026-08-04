from __future__ import annotations

import pytest

from app.media.exceptions import MediaTooLarge, UnsupportedMedia
from app.media.models import MediaPrepareRequest, MediaType
from app.media.service import MediaService


def test_service_validation_rejects_large_media() -> None:
    service = MediaService(max_media_size=3)

    with pytest.raises(MediaTooLarge):
        service.create_metadata(MediaPrepareRequest(type=MediaType.DOCUMENT), b"toolong")


def test_service_validation_rejects_unsupported_mime() -> None:
    service = MediaService()

    with pytest.raises(UnsupportedMedia):
        service.create_metadata(
            MediaPrepareRequest(type=MediaType.PHOTO, filename="notes.txt"),
            b"plain text",
        )


def test_prepare_upload_returns_operation_descriptor() -> None:
    service = MediaService()
    operation = service.prepare_upload(
        MediaPrepareRequest(type=MediaType.DOCUMENT, filename="doc.pdf"),
        b"%PDF-1.7",
    )

    assert operation.ready is True
    assert operation.storage_key == f"document/{operation.media_id}"
    assert operation.metadata.mime_type == "application/pdf"
