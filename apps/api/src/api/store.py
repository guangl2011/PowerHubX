"""SQLite persistence for projects and stored simulation results (design doc §2).

One project record carries the intake data (name, location, the SiteProfile
JSON and its version) plus the last simulate run's metrics as JSON. Sessions
are provided to routes through ``get_session``, which reads the session
factory off ``app.state`` — the app factory owns the one DB path decision.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DB_PATH_ENV_VAR = "POWERHUBX_DB_PATH"
DEFAULT_DB_PATH = "powerhubx.db"


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    # Naive UTC: SQLite stores no timezone; MVP treats all timestamps as UTC.
    return datetime.now(UTC).replace(tzinfo=None)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(primary_key=True)  # uuid4 hex
    name: Mapped[str | None]
    location: Mapped[str | None]
    # Canonical SiteProfile JSON (SiteProfileIn.model_dump_json), absent until
    # the wizard submits — the engine contract's "no site yet" state.
    site_json: Mapped[str | None]
    site_version: Mapped[int]
    # StoredResults JSON from the last simulate run, absent until one runs.
    results_json: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=_utcnow, onupdate=_utcnow)


def resolve_db_path(db_path: str | None) -> str:
    return db_path or os.environ.get(DB_PATH_ENV_VAR) or DEFAULT_DB_PATH


def make_engine(db_path: str) -> Engine:
    # check_same_thread=False: FastAPI runs sync endpoints on a threadpool
    # against one file-backed engine; SQLite connections are per-session.
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def get_session(request: Request) -> Iterator[Session]:
    factory: sessionmaker[Session] = request.app.state.session_factory
    session = factory()
    try:
        yield session
    finally:
        session.close()
