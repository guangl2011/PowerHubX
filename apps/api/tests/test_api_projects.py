"""Project store and site-profile endpoints: create, get, PUT /site validation."""

from __future__ import annotations

import json
from typing import Any

from fastapi.testclient import TestClient


def _error_fields(body: dict[str, Any]) -> set[str]:
    """Field names FastAPI flagged in a 422 body: {loc: ("body", field, ...)}."""
    return {str(entry["loc"][1]) for entry in body["detail"] if len(entry["loc"]) > 1}


def test_create_project_without_site(client: TestClient) -> None:
    response = client.post(
        "/api/projects", json={"name": "Hill Country AIDC", "location": "Texas"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Hill Country AIDC"
    assert body["location"] == "Texas"
    assert body["site"] is None
    assert body["site_version"] == 0
    assert body["has_results"] is False
    assert body["created_at"] and body["updated_at"]


def test_create_project_with_site(client: TestClient, site_payload: dict[str, Any]) -> None:
    response = client.post("/api/projects", json={"name": "P1", "site": site_payload})
    assert response.status_code == 201
    body = response.json()
    assert body["site_version"] == 1
    assert body["site"] == site_payload


def test_get_project_roundtrip(client: TestClient, project_id: str) -> None:
    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id


def test_get_missing_project_404(client: TestClient) -> None:
    response = client.get("/api/projects/nope")
    assert response.status_code == 404


def test_put_site_bumps_version(
    client: TestClient, project_id: str, site_payload: dict[str, Any]
) -> None:
    first = client.put(f"/api/projects/{project_id}/site", json=site_payload)
    assert first.status_code == 200
    assert first.json()["site_version"] == 1
    assert first.json()["site"] == site_payload

    second = client.put(f"/api/projects/{project_id}/site", json=site_payload)
    assert second.status_code == 200
    assert second.json()["site_version"] == 2


def test_put_site_rejects_negative_mw(
    client: TestClient, project_id: str, site_payload: dict[str, Any]
) -> None:
    payload = dict(site_payload, grid_limit_mw=-1.0)
    response = client.put(f"/api/projects/{project_id}/site", json=payload)
    assert response.status_code == 422
    assert "grid_limit_mw" in _error_fields(response.json())
    # The project keeps its no-site state after a rejected submission.
    assert client.get(f"/api/projects/{project_id}").json()["site"] is None


def test_put_site_rejects_missing_fields(client: TestClient, project_id: str) -> None:
    response = client.put(f"/api/projects/{project_id}/site", json={"grid_limit_mw": 10.0})
    assert response.status_code == 422
    flagged = _error_fields(response.json())
    assert {"it_load_mw", "flexible_share", "tariff_usd_kwh"} <= flagged


def test_put_site_rejects_bad_criticality(
    client: TestClient, project_id: str, site_payload: dict[str, Any]
) -> None:
    payload = dict(site_payload, criticality="tier9")
    response = client.put(f"/api/projects/{project_id}/site", json=payload)
    assert response.status_code == 422
    assert "criticality" in _error_fields(response.json())


def test_put_site_rejects_bad_date(
    client: TestClient, project_id: str, site_payload: dict[str, Any]
) -> None:
    payload = dict(site_payload, target_energization="06/2027")
    response = client.put(f"/api/projects/{project_id}/site", json=payload)
    assert response.status_code == 422
    assert "target_energization" in _error_fields(response.json())


def test_put_site_rejects_share_out_of_range(
    client: TestClient, project_id: str, site_payload: dict[str, Any]
) -> None:
    payload = dict(site_payload, flexible_share=1.5)
    response = client.put(f"/api/projects/{project_id}/site", json=payload)
    assert response.status_code == 422
    assert "flexible_share" in _error_fields(response.json())


def test_put_site_rejects_non_finite_numbers(
    client: TestClient, project_id: str, site_payload: dict[str, Any]
) -> None:
    # json.dumps emits Infinity for float("inf"); the API must refuse it.
    raw = json.dumps(site_payload).replace(
        '"grid_limit_mw": 50.0', '"grid_limit_mw": Infinity'
    )
    response = client.put(
        f"/api/projects/{project_id}/site",
        content=raw,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert "grid_limit_mw" in _error_fields(response.json())


def test_put_site_to_missing_project_404(
    client: TestClient, site_payload: dict[str, Any]
) -> None:
    response = client.put("/api/projects/nope/site", json=site_payload)
    assert response.status_code == 404
