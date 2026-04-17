from fastapi import APIRouter, HTTPException, status
from sqlmodel import func, select

from app.api.dependencies import CurrentUserDep, SessionDep
from app.api.schemas import PaginatedResponse, ProjectCreate, ProjectResponse
from app.models import Project
from app.utils.pagination import create_paginated_response
from app.utils.soft_delete import filter_active, soft_delete

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=PaginatedResponse[ProjectResponse])
def list_projects(
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = 1,
    page_size: int = 20,
):
    """プロジェクト一覧取得（ページネーション付き）"""
    # ベースクエリ
    base_query = select(Project).where(Project.owner_id == current_user.id)
    base_query = filter_active(base_query, Project)

    # 総件数を取得
    count_query = select(func.count()).select_from(base_query.subquery())
    total = session.exec(count_query).one()

    # ページネーションを適用
    offset = (page - 1) * page_size
    query = base_query.offset(offset).limit(page_size)
    projects = session.exec(query).all()

    return create_paginated_response(
        items=projects, total=total, page=page, page_size=page_size
    )


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
