"""The full happy-path flow over httpx (TestClient): wizard intake to report.

One customer run end to end — create, submit site, simulate, ranked results,
sensitivity sweep, report — plus the 404 contract every endpoint shares.
"""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient


def test_full_happy_path(client: TestClient, site_payload: dict[str, Any]) -> None:
    # 1. Create from the wizard payload.
    created = client.post(
        "/api/projects",
        json={"name": "Downtown colo", "location": "Ashburn, VA", "site": site_payload},
    )
    assert created.status_code == 201
    pid = created.json()["id"]
    assert created.json()["site_version"] == 1

    # 2. Simulate all four architectures.
    simulated = client.post(f"/api/projects/{pid}/simulate")
    assert simulated.status_code == 200
    ranking = simulated.json()["ranking"]
    assert len(ranking) == 4
    assert simulated.json()["stale"] is False

    # 3. Results endpoint serves the same ranked comparison.
    results = client.get(f"/api/projects/{pid}/results")
    assert results.status_code == 200
    assert [r["architecture"] for r in results.json()["ranking"]] == [
        r["architecture"] for r in ranking
    ]

    # 4. Sensitivity sweep over GPU utilization.
    swept = client.post(
        f"/api/projects/{pid}/sensitivity",
        json={"param": "gpu_utilization", "range": [0.6, 0.8, 1.0]},
    )
    assert swept.status_code == 200
    assert len(swept.json()["points"]) == 12  # 3 values x 4 architectures

    # 5. The report carries the five evaluation axes end to end.
    report = client.get(f"/api/projects/{pid}/report")
    assert report.status_code == 200
    assert report.headers["content-type"].startswith("text/html")
    assert "Downtown colo" in report.text and "Ashburn, VA" in report.text
    for label in (
        "Chain efficiency",
        "Cost per delivered MWh ($/MWh)",
        "Time to power (months)",
        "Resilience score (0-1)",
        "Carbon intensity (kg CO2/kWh)",
    ):
        assert label in report.text

    # Cross-endpoint consistency: has_results reflects the stored run.
    assert client.get(f"/api/projects/{pid}").json()["has_results"] is True


def test_site_change_marks_results_stale_until_resimulated(
    client: TestClient, site_payload: dict[str, Any]
) -> None:
    created = client.post("/api/projects", json={"name": "Stale check"}).json()
    client.put(f"/api/projects/{created['id']}/site", json=site_payload)
    client.post(f"/api/projects/{created['id']}/simulate")
    client.put(
        f"/api/projects/{created['id']}/site", json=dict(site_payload, flexible_share=0.5)
    )
    stale = client.get(f"/api/projects/{created['id']}/results").json()
    assert stale["stale"] is True
    fresh = client.post(f"/api/projects/{created['id']}/simulate").json()
    assert fresh["stale"] is False


def test_unknown_project_404_on_every_endpoint(client: TestClient, site_payload: dict) -> None:
    assert client.get("/api/projects/nope").status_code == 404
    assert client.put("/api/projects/nope/site", json=site_payload).status_code == 404
    assert client.post("/api/projects/nope/simulate").status_code == 404
    assert client.get("/api/projects/nope/results").status_code == 404
    assert client.post(
        "/api/projects/nope/sensitivity", json={"param": "tariff_usd_kwh", "range": [0.1]}
    ).status_code == 404
    assert client.get("/api/projects/nope/report").status_code == 404


def test_two_projects_are_independent(client: TestClient, site_payload: dict) -> None:
    first = client.post("/api/projects", json={"name": "A"}).json()
    second = client.post("/api/projects", json={"name": "B"}).json()
    client.put(f"/api/projects/{first['id']}/site", json=site_payload)
    # Second project still has no site; first is unaffected.
    assert client.post(f"/api/projects/{second['id']}/simulate").status_code == 409
    assert client.get(f"/api/projects/{first['id']}").json()["site_version"] == 1
    assert client.get(f"/api/projects/{second['id']}").json()["site_version"] == 0
