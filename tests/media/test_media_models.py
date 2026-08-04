from __future__ import annotations

from app.media.models import MediaPrepareRequest, MediaType, Photo
from app.media.service import MediaService


def test_metadata_creation_uses_typed_model() -> None:
    service = MediaService()
    metadata = service.create_metadata(
        MediaPrepareRequest(type=MediaType.PHOTO, filename="sample.jpg"),
        b"\xff\xd8\xffcontent",
    )

    assert isinstance(metadata, Photo)
    assert metadata.type == MediaType.PHOTO
    assert metadata.mime_type == "image/jpeg"
    assert metadata.filename == "sample.jpg"
    assert metadata.size == 10
    assert len(metadata.sha256) == 64
