from __future__ import annotations


def test_media_types_endpoint(client) -> None:
    response = client.get("/api/v1/media/types")

    assert response.status_code == 200
    assert "photo" in response.json()
    assert "document" in response.json()


def test_media_storage_provider_endpoint(client) -> None:
    response = client.get("/api/v1/media/storage/provider")

    assert response.status_code == 200
    assert response.json()["provider"] in {"local", "memory"}


def test_media_storage_info_endpoint(client) -> None:
    response = client.get("/api/v1/media/storage/info")

    assert response.status_code == 200
    assert "provider" in response.json()


def test_mock_media_metadata_endpoint(client) -> None:
    response = client.get("/api/v1/media/example")

    assert response.status_code == 200
    payload = response.json()
    assert payload["type"] == "document"
    assert payload["filename"] == "example.bin"


def test_mock_media_delete_endpoint(client) -> None:
    response = client.delete("/api/v1/media/example")

    assert response.status_code == 204
