from __future__ import annotations


def test_dashboard_endpoints_require_auth(client) -> None:
    for path in ("/dashboard/overview", "/dashboard/logs", "/dashboard/metrics"):
        response = client.get(path)
        assert response.status_code == 401


def test_dashboard_overview_for_authenticated_user(client) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    response = client.get(
        "/dashboard/overview",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["platform"] == "BerTele2"
    assert "stats" in payload
    assert "sessions" in payload["stats"]


def test_dashboard_logs_and_metrics_for_authenticated_user(client) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logs_response = client.get("/dashboard/logs", headers=headers)
    metrics_response = client.get("/dashboard/metrics", headers=headers)

    assert logs_response.status_code == 200, logs_response.text
    assert metrics_response.status_code == 200, metrics_response.text
    assert isinstance(logs_response.json()["items"], list)
    assert isinstance(metrics_response.json()["series"], list)
