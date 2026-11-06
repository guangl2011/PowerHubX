"""API smoke tests for the bootstrap: the app factory and health endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import create_app


def test_healthz_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "powerhubx-api"
