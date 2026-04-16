from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.dependencies import CurrentUserDep, SessionDep, verify_project_access
from app.api.schemas import SprintCreate, SprintResponse
from app.models import Sprint

router = APIRouter(tags=["sprints"])


@router.get("/projects/{project_id}/sprints", response_model=List[SprintResponse])
def list_sprints(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
    limit: int = 50,
    offset: int = 0,
):
    verify_project_access(project_id, current_user, session)
    sprints = session.exec(
        select(Sprint)
        .where(Sprint.project_id == project_id)
        .offset(offset)
        .limit(limit)
    ).all()
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
    verify_project_access(project_id, current_user, session)
    sprint = Sprint(project_id=project_id, **body.model_dump())
    session.add(sprint)
    session.commit()
    session.refresh(sprint)
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
    verify_project_access(project_id, current_user, session)
    sprint = session.get(Sprint, sprint_id)
    if not sprint or sprint.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
        )
    session.delete(sprint)
    session.commit()


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
    verify_project_access(project_id, current_user, session)
    sprint = session.get(Sprint, sprint_id)
    if not sprint or sprint.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
        )

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sprint, key, value)

    session.add(sprint)
    session.commit()
    session.refresh(sprint)
    return sprint
