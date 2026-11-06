"""FastAPI application factory.

Bootstrap scaffold: a health endpoint only. Project store, simulation
orchestration, and report export arrive in later PRs (spec art_Xihp9Qa2,
API shape section).
"""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="PowerHubX API",
        version="0.1.0",
        description=(
            "Feasibility-to-onboarding API for AIDC and microgrid power architecture decisions."
        ),
    )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok", "service": "powerhubx-api", "version": "0.1.0"}

    return app


app = create_app()
