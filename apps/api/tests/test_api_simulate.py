"""Simulate and results endpoints: orchestration, ranking, staleness."""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

ALL_ARCHITECTURES = {"grid-only", "grid+bess", "mvdc-sst-hybrid", "islandable-microgrid"}


def test_simulate_without_site_409(client: TestClient, project_id: str) -> None:
    response = client.post(f"/api/projects/{project_id}/simulate")
    assert response.status_code == 409
    assert "site" in response.json()["detail"].lower()


def test_simulate_missing_project_404(client: TestClient) -> None:
    response = client.post("/api/projects/nope/simulate")
    assert response.status_code == 404


def test_simulate_all_default(client: TestClient, sited_project_id: str) -> None:
    response = client.post(f"/api/projects/{sited_project_id}/simulate")
    assert response.status_code == 200
    body = response.json()
    assert {r["architecture"] for r in body["ranking"]} == ALL_ARCHITECTURES
    assert body["stale"] is False
    assert body["site_version"] == 1
    # Scores sorted best-first; per-axis scores carry the five-axis vocabulary.
    scores = [r["score"] for r in body["ranking"]]
    assert scores == sorted(scores, reverse=True)
    assert set(body["weights"]) == set(body["ranking"][0]["axis_scores"])
    # Every scenario carries the five axes plus the dispatch split behind it.
    metrics = body["ranking"][0]["metrics"]
    assert {"chain_efficiency", "cost_per_mwh", "time_to_power_months",
            "resilience_score", "carbon_kgCO2_kWh"} <= set(metrics)
    assert set(metrics["dispatch"]) == {
        "curtailed_gpu_mwh", "shed_mwh", "curtailed_hours", "shed_hours"
    }


def test_simulate_selected_subset(client: TestClient, sited_project_id: str) -> None:
    response = client.post(
        f"/api/projects/{sited_project_id}/simulate",
        json={"architectures": ["grid-only", "mvdc-sst-hybrid"]},
    )
    assert response.status_code == 200
    names = {r["architecture"] for r in response.json()["ranking"]}
    assert names == {"grid-only", "mvdc-sst-hybrid"}


def test_simulate_unknown_architecture_422(client: TestClient, sited_project_id: str) -> None:
    response = client.post(
        f"/api/projects/{sited_project_id}/simulate",
        json={"architectures": ["nuclear-fusion"]},
    )
    assert response.status_code == 422
    assert "nuclear-fusion" in response.json()["detail"][0]["msg"]


def test_results_before_simulate_409(client: TestClient, sited_project_id: str) -> None:
    response = client.get(f"/api/projects/{sited_project_id}/results")
    assert response.status_code == 409


def test_results_roundtrip_ranked(client: TestClient, sited_project_id: str) -> None:
    simulated = client.post(f"/api/projects/{sited_project_id}/simulate").json()
    fetched = client.get(f"/api/projects/{sited_project_id}/results")
    assert fetched.status_code == 200
    assert [r["architecture"] for r in fetched.json()["ranking"]] == [
        r["architecture"] for r in simulated["ranking"]
    ]


def test_ranking_deterministic(client: TestClient, sited_project_id: str) -> None:
    first = client.post(f"/api/projects/{sited_project_id}/simulate").json()
    second = client.post(f"/api/projects/{sited_project_id}/simulate").json()
    assert [r["architecture"] for r in first["ranking"]] == [
        r["architecture"] for r in second["ranking"]
    ]
    assert first["ranking"][0]["score"] == second["ranking"][0]["score"]


def test_core_claim_visible_through_api(client: TestClient, sited_project_id: str) -> None:
    # The product's core claim (spec D2) must hold in what the API serves.
    body = client.post(f"/api/projects/{sited_project_id}/simulate").json()
    by_name = {r["architecture"]: r["metrics"] for r in body["ranking"]}
    assert (
        by_name["mvdc-sst-hybrid"]["chain_efficiency"]
        > by_name["grid-only"]["chain_efficiency"]
    )


def test_results_stale_after_site_change(
    client: TestClient, sited_project_id: str, site_payload: dict[str, Any]
) -> None:
    client.post(f"/api/projects/{sited_project_id}/simulate")
    client.put(
        f"/api/projects/{sited_project_id}/site", json=dict(site_payload, it_load_mw=35.0)
    )
    body = client.get(f"/api/projects/{sited_project_id}/results").json()
    assert body["stale"] is True
    assert body["site_version"] == 1  # the run's version, not the project's

    refreshed = client.post(f"/api/projects/{sited_project_id}/simulate").json()
    assert refreshed["stale"] is False
    assert refreshed["site_version"] == 2


def test_get_results_missing_project_404(client: TestClient) -> None:
    assert client.get("/api/projects/nope/results").status_code == 404
