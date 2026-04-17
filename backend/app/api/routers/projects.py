from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.dependencies import CurrentUserDep, SessionDep
from app.api.schemas import ProjectCreate, ProjectResponse
from app.models import Project
from app.utils.soft_delete import soft_delete, filter_active

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    session: SessionDep,
    current_user: CurrentUserDep,
    limit: int = 20,
    offset: int = 0,
):
    query = select(Project).where(Project.owner_id == current_user.id)
    # ソフトデリートされたプロジェクトを除外
    query = filter_active(query, Project)
    projects = session.exec(query.offset(offset).limit(limit)).all()
    return projects


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """プロジェクト作成"""
    project = Project(
        name=body.name,
        description=body.description,
        owner_id=current_user.id,
    )
    try:
        session.add(project)
        session.commit()
        session.refresh(project)
    except Exception:
        session.rollback()
        raise
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    project = session.get(Project, project_id)
    if not project or project.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """プロジェクト削除（ソフトデリート）"""
    project = session.get(Project, project_id)
    if not project or project.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    try:
        # ソフトデリートを実行
        soft_delete(session, project)
    except Exception:
        session.rollback()
        raise
