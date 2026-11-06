"""Sensitivity endpoint: one axis swept into a result matrix."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_sensitivity_happy(client: TestClient, sited_project_id: str) -> None:
    response = client.post(
        f"/api/projects/{sited_project_id}/sensitivity",
        json={
            "param": "gpu_utilization",
            "range": [0.5, 1.0],
            "architectures": ["grid-only", "mvdc-sst-hybrid"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["param"] == "gpu_utilization"
    assert body["values"] == [0.5, 1.0]
    assert body["architectures"] == ["grid-only", "mvdc-sst-hybrid"]
    assert len(body["points"]) == 4  # 2 values x 2 architectures
    assert {p["architecture"] for p in body["points"]} == {"grid-only", "mvdc-sst-hybrid"}
    assert all(p["axis"] == "gpu_utilization" for p in body["points"])
    assert {p["value"] for p in body["points"]} == {0.5, 1.0}
    # Points carry the scalar five-axis metrics, no hourly series.
    assert "cost_per_mwh" in body["points"][0]
    assert "hourly" not in body["points"][0]


def test_sensitivity_defaults_to_all_architectures(
    client: TestClient, sited_project_id: str
) -> None:
    response = client.post(
        f"/api/projects/{sited_project_id}/sensitivity",
        json={"param": "tariff_usd_kwh", "range": [0.06, 0.1]},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["points"]) == 8  # 2 values x 4 architectures
    assert len(body["architectures"]) == 4


def test_sensitivity_unknown_param_422(client: TestClient, sited_project_id: str) -> None:
    response = client.post(
        f"/api/projects/{sited_project_id}/sensitivity",
        json={"param": "gpu_price", "range": [0.5]},
    )
    assert response.status_code == 422
    assert "gpu_price" in response.json()["detail"][0]["msg"]


def test_sensitivity_negative_value_422(client: TestClient, sited_project_id: str) -> None:
    response = client.post(
        f"/api/projects/{sited_project_id}/sensitivity",
        json={"param": "tariff_usd_kwh", "range": [-0.05]},
    )
    assert response.status_code == 422


def test_sensitivity_oversized_range_422(client: TestClient, sited_project_id: str) -> None:
    response = client.post(
        f"/api/projects/{sited_project_id}/sensitivity",
        json={"param": "tariff_usd_kwh", "range": [0.05] * 101},
    )
    assert response.status_code == 422


def test_sensitivity_without_site_409(client: TestClient, project_id: str) -> None:
    response = client.post(
        f"/api/projects/{project_id}/sensitivity",
        json={"param": "tariff_usd_kwh", "range": [0.05]},
    )
    assert response.status_code == 409


def test_sensitivity_missing_project_404(client: TestClient) -> None:
    response = client.post(
        "/api/projects/nope/sensitivity",
        json={"param": "tariff_usd_kwh", "range": [0.05]},
    )
    assert response.status_code == 404
