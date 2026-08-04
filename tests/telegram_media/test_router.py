from __future__ import annotations

from app.media.models import MediaMetadata, MediaType
from app.telegram.media.downloader import MediaResource
from app.telegram.media.router import get_telegram_media_service


class FakeTelegramMediaService:
    async def download(self, media, *, session_id: str = "default") -> MediaResource:
        metadata = MediaMetadata(
            type=MediaType.DOCUMENT,
            mime_type="application/pdf",
            filename="doc.pdf",
            size=5,
            sha256="x" * 64,
            telegram_file_id=media["file_reference"],
        )
        return MediaResource(metadata=metadata, storage_key=f"document/{metadata.id}")


def test_download_endpoint(client) -> None:
    client.app.dependency_overrides[get_telegram_media_service] = lambda: FakeTelegramMediaService()
    try:
        response = client.post(
            "/api/v1/telegram/media/download",
            json={
                "media": {"type": "document", "file_reference": "doc-ref"},
                "session_id": "default",
            },
        )
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"]["telegram_file_id"] == "doc-ref"
    assert payload["storage_key"].startswith("document/")
