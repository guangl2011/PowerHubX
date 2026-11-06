"""Report endpoint: one-page HTML feasibility report from stored results."""

from __future__ import annotations

from fastapi.testclient import TestClient

FIVE_AXIS_LABELS = (
    "Chain efficiency",
    "Cost per delivered MWh ($/MWh)",
    "Time to power (months)",
    "Resilience score (0-1)",
    "Carbon intensity (kg CO2/kWh)",
)

ALL_ARCHITECTURES = ("grid-only", "grid+bess", "mvdc-sst-hybrid", "islandable-microgrid")


def _simulate(client: TestClient, project_id: str) -> None:
    response = client.post(f"/api/projects/{project_id}/simulate")
    assert response.status_code == 200


def test_report_happy_html(client: TestClient, sited_project_id: str) -> None:
    _simulate(client, sited_project_id)
    response = client.get(f"/api/projects/{sited_project_id}/report")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    html = response.text
    for label in FIVE_AXIS_LABELS:
        assert label in html, f"missing evaluation axis: {label}"
    for architecture in ALL_ARCHITECTURES:
        assert architecture in html, f"missing architecture: {architecture}"
    assert "Recommended architecture" in html
    # The scoping disclaimer must be on the page: placeholder assumptions only.
    assert "placeholder assumptions" in html


def test_report_shows_site_facts(client: TestClient, sited_project_id: str) -> None:
    _simulate(client, sited_project_id)
    html = client.get(f"/api/projects/{sited_project_id}/report").text
    assert "132.0" in html  # rack density from the reference profile
    assert "2027-06-01" in html  # target energization


def test_report_escapes_user_input(client: TestClient, site_payload: dict) -> None:
    created = client.post(
        "/api/projects", json={"name": "<script>alert(1)</script>", "location": "<b>TX</b>"}
    ).json()
    client.put(f"/api/projects/{created['id']}/site", json=site_payload)
    _simulate(client, created["id"])
    html = client.get(f"/api/projects/{created['id']}/report").text
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_report_warns_when_stale(
    client: TestClient, sited_project_id: str, site_payload: dict
) -> None:
    _simulate(client, sited_project_id)
    client.put(
        f"/api/projects/{sited_project_id}/site", json=dict(site_payload, it_load_mw=35.0)
    )
    html = client.get(f"/api/projects/{sited_project_id}/report").text
    assert "Warning" in html


def test_report_before_simulate_409(client: TestClient, sited_project_id: str) -> None:
    response = client.get(f"/api/projects/{sited_project_id}/report")
    assert response.status_code == 409


def test_report_missing_project_404(client: TestClient) -> None:
    assert client.get("/api/projects/nope/report").status_code == 404
