"""Project store and site-profile endpoints (spec art_Xihp9Qa2, API shape).

Routes own orchestration and error mapping only: 404 unknown project, 409
state conflicts (no site), 422 body validation (pydantic, with field
errors). All math is delegated to the engine.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api import store
from api.schemas import ProjectCreate, ProjectOut, SiteProfileIn

router = APIRouter(prefix="/api")

SessionDep = Depends(store.get_session)


def _project_or_404(session: Session, project_id: str) -> store.Project:
    project = session.get(store.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"project {project_id} not found")
    return project


def _site_or_409(project: store.Project) -> SiteProfileIn:
    if project.site_json is None:
        raise HTTPException(
            status_code=409,
            detail="project has no site profile yet — submit one via PUT /api/projects/{id}/site",
        )
    return SiteProfileIn.model_validate_json(project.site_json)


def _project_out(project: store.Project) -> ProjectOut:
    site = (
        SiteProfileIn.model_validate_json(project.site_json)
        if project.site_json is not None
        else None
    )
    return ProjectOut(
        id=project.id,
        name=project.name,
        location=project.location,
        site=site,
        site_version=project.site_version,
        has_results=project.results_json is not None,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post("/projects", status_code=201)
def create_project(payload: ProjectCreate, session: Session = SessionDep) -> ProjectOut:
    project = store.Project(
        id=uuid.uuid4().hex,
        name=payload.name,
        location=payload.location,
        site_json=payload.site.model_dump_json() if payload.site else None,
        site_version=1 if payload.site else 0,
        results_json=None,
    )
    session.add(project)
    session.commit()
    return _project_out(project)


@router.get("/projects/{project_id}")
def get_project(project_id: str, session: Session = SessionDep) -> ProjectOut:
    return _project_out(_project_or_404(session, project_id))


@router.put("/projects/{project_id}/site")
def replace_site(
    project_id: str, profile: SiteProfileIn, session: Session = SessionDep
) -> ProjectOut:
    project = _project_or_404(session, project_id)
    project.site_json = profile.model_dump_json()
    project.site_version += 1  # the stored run's results go stale via this bump
    session.commit()
    return _project_out(project)
