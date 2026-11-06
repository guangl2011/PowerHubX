"""Shared API test fixtures: an isolated SQLite DB and client per test.

The reference site payload mirrors engine/tests/conftest.py
REFERENCE_PROFILE (the engine's own fixture source of truth) so API tests
exercise the same site the engine tests do.

API test FILES carry an ``api_`` infix (test_api_*.py): pytest imports test
modules by basename without packages, so a name shared with engine/tests
(test_sensitivity.py) collides at collection time. root mypy config excludes
tests/ dirs for the same basename-mapping reason.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from api.main import create_app

REFERENCE_PROFILE: dict[str, Any] = {
    "grid_limit_mw": 50.0,
    "it_load_mw": 30.0,
    "flexible_share": 0.3,
    "rack_density_kw": 132.0,
    "criticality": "tier3",
    "bess_mwh": 100.0,
    "pv_mw": 10.0,
    "fuel_cell_mw": 5.0,
    "genset_mw": 5.0,
    "tariff_usd_kwh": 0.08,
    "interconnection_wait_months": 36,
    "target_energization": "2027-06-01",
}


@pytest.fixture
def client(tmp_path: Any) -> Iterator[TestClient]:
    # Context manager runs the app lifespan, so the engine is disposed on
    # teardown — no pooled SQLite connection outlives the test.
    with TestClient(create_app(db_path=str(tmp_path / "api-test.db"))) as test_client:
        yield test_client


@pytest.fixture
def site_payload() -> dict[str, Any]:
    return dict(REFERENCE_PROFILE)


@pytest.fixture
def project_id(client: TestClient) -> str:
    """A created project with no site profile yet."""
    response = client.post(
        "/api/projects", json={"name": "Test site", "location": "Austin, TX"}
    )
    assert response.status_code == 201
    return str(response.json()["id"])


@pytest.fixture
def sited_project_id(
    client: TestClient, project_id: str, site_payload: dict[str, Any]
) -> str:
    """A project whose site profile has been submitted."""
    response = client.put(f"/api/projects/{project_id}/site", json=site_payload)
    assert response.status_code == 200
    return project_id
