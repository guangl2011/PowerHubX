"""FastAPI application factory.

Wires the SQLite session factory (path: argument, POWERHUBX_DB_PATH, or
./powerhubx.db) and the /api routes. The bootstrap /healthz contract is kept.
Project store, simulation orchestration, and report export are the MVP
endpoints (spec art_Xihp9Qa2, API shape section).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.engine import Engine

from api import store
from api.routes import router

API_VERSION = "0.1.0"


async def sanitized_validation_errors(request: Request, exc: Exception) -> JSONResponse:
    """422 with field loc + message only.

    FastAPI's default body echoes the offending ``input`` value — which can be
    inf/NaN and then crashes Starlette's allow_nan=False JSON serializer
    before the 422 ever leaves the app. Never echo raw input back.
    """
    # Starlette's handler registry passes Exception; this handler is
    # registered for RequestValidationError only.
    validation_error = cast(RequestValidationError, exc)
    detail = [
        {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
        for error in validation_error.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": detail})


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # The app owns the engine it created; dispose pooled connections on
    # shutdown so nothing outlives the process (ASGI teardown and tests).
    yield
    engine: Engine = app.state.engine
    engine.dispose()


def create_app(db_path: str | None = None) -> FastAPI:
    engine = store.make_engine(store.resolve_db_path(db_path))
    app = FastAPI(
        title="PowerHubX API",
        version=API_VERSION,
        description=(
            "Feasibility-to-onboarding API for AIDC and microgrid power architecture decisions."
        ),
        lifespan=lifespan,
    )
    app.state.engine = engine
    app.state.session_factory = store.make_session_factory(engine)
    app.include_router(router)
    app.add_exception_handler(RequestValidationError, sanitized_validation_errors)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok", "service": "powerhubx-api", "version": API_VERSION}

    return app


app = create_app()
