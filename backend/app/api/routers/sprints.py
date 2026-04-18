from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.dependencies import CurrentUserDep, SessionDep, verify_project_access
from app.api.schemas import SprintCreate, SprintResponse
from app.models import Sprint
from app.utils.soft_delete import filter_active, soft_delete

router = APIRouter(tags=["sprints"])


@router.get("/projects/{project_id}/sprints", response_model=list[SprintResponse])
def list_sprints(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
    limit: int = 50,
    offset: int = 0,
):
    verify_project_access(project_id, current_user, session)
    base_query = select(Sprint).where(Sprint.project_id == project_id)
    base_query = filter_active(base_query, Sprint)
    sprints = session.exec(base_query.offset(offset).limit(limit)).all()
    return sprints


@router.post(
    "/projects/{project_id}/sprints",
    response_model=SprintResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sprint(
    project_id: int,
    body: SprintCreate,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """スプリント作成"""
    verify_project_access(project_id, current_user, session)
    sprint = Sprint(project_id=project_id, **body.model_dump())
    try:
        session.add(sprint)
        session.commit()
        session.refresh(sprint)
    except Exception:
        session.rollback()
        raise
    return sprint


@router.delete(
    "/projects/{project_id}/sprints/{sprint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_sprint(
    project_id: int,
    sprint_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """スプリント削除（ソフトデリート）"""
    verify_project_access(project_id, current_user, session)
    sprint = session.get(Sprint, sprint_id)
    if not sprint or sprint.project_id != project_id or sprint.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
        )
    try:
        soft_delete(session, sprint)
    except Exception:
        session.rollback()
        raise


@router.put(
    "/projects/{project_id}/sprints/{sprint_id}",
    response_model=SprintResponse,
)
def update_sprint(
    project_id: int,
    sprint_id: int,
    body: SprintCreate,  # SprintUpdateスキーマを別途作るほどでもないので再利用
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """スプリント更新"""
    verify_project_access(project_id, current_user, session)
    sprint = session.get(Sprint, sprint_id)
    if not sprint or sprint.project_id != project_id or sprint.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
        )

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sprint, key, value)

    try:
        session.add(sprint)
        session.commit()
        session.refresh(sprint)
    except Exception:
        session.rollback()
        raise
    return sprint
