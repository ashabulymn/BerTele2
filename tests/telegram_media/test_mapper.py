from __future__ import annotations

import pytest

from app.media.models import MediaType
from app.telegram.media.mapper import InvalidTelegramMedia, TelegramMediaMapper


@pytest.mark.parametrize(
    ("media", "expected_type"),
    [
        ({"type": "photo", "file_reference": "photo-ref"}, MediaType.PHOTO),
        ({"type": "video", "file_reference": "video-ref"}, MediaType.VIDEO),
        ({"type": "document", "file_reference": "doc-ref"}, MediaType.DOCUMENT),
        ({"type": "audio", "file_reference": "audio-ref"}, MediaType.AUDIO),
        ({"type": "voice", "file_reference": "voice-ref"}, MediaType.VOICE),
        ({"type": "animation", "file_reference": "animation-ref"}, MediaType.ANIMATION),
        ({"type": "sticker", "file_reference": "sticker-ref"}, MediaType.STICKER),
    ],
)
def test_mapper_supports_media_types(media, expected_type) -> None:
    mapping = TelegramMediaMapper().map(media)

    assert mapping.payload.type == expected_type
    assert mapping.file_reference == media["file_reference"]


def test_mapper_rejects_missing_file_reference() -> None:
    with pytest.raises(InvalidTelegramMedia):
        TelegramMediaMapper().map({"type": "photo"})
