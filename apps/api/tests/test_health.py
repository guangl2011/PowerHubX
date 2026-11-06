"""API smoke tests for the bootstrap: the app factory and health endpoint."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.main import create_app


def test_healthz_ok(tmp_path: Path) -> None:
    # Context manager runs the app lifespan so the engine disposes on exit;
    # tmp_path keeps the test from creating ./powerhubx.db in the repo.
    with TestClient(create_app(db_path=str(tmp_path / "healthz.db"))) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "powerhubx-api"
