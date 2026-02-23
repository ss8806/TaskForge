from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.dependencies import CurrentUserIdDep, SessionDep
from app.api.schemas import ProjectCreate, ProjectResponse
from app.models import Project

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
    limit: int = 20,
    offset: int = 0,
):
    projects = session.exec(
        select(Project)
        .where(Project.owner_id == current_user_id)
        .offset(offset)
        .limit(limit)
    ).all()
    return projects


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
):
    project = Project(
        name=body.name,
        description=body.description,
        owner_id=current_user_id,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    session.delete(project)
    session.commit()
