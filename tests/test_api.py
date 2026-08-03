from __future__ import annotations


def test_health_endpoint(client) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_endpoint(client) -> None:
    response = client.get("/api/v1/version")

    assert response.status_code == 200
    payload = response.json()
    assert payload["app_name"] == "BerTele2"
    assert payload["version"] == "0.1.0"


def test_openapi_is_exposed(client) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/health" in response.text
