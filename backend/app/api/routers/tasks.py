from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.dependencies import CurrentUserIdDep, SessionDep
from app.api.schemas import TaskCreate, TaskResponse, TaskUpdate
from app.models import Project, Task

router = APIRouter(tags=["tasks"])


def _verify_project_access(project_id: int, user_id: int, session) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return project


# ── プロジェクト配下のタスクCRUD ─────────────────────────────────────────────

@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
def list_tasks(
    project_id: int,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
    limit: int = 100,
    offset: int = 0,
    status: str | None = None,
    sprint_id: int | None = None,
):
    _verify_project_access(project_id, current_user_id, session)
    query = select(Task).where(Task.project_id == project_id)
    if status is not None:
        query = query.where(Task.status == status)
    if sprint_id is not None:
        query = query.where(Task.sprint_id == sprint_id)
    query = query.offset(offset).limit(limit)
    tasks = session.exec(query).all()
    return tasks


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=201,
)
def create_task(
    project_id: int,
    body: TaskCreate,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
):
    _verify_project_access(project_id, current_user_id, session)
    task = Task(project_id=project_id, **body.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# ── 個別タスク操作 ────────────────────────────────────────────────────────────

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    body: TaskUpdate,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    _verify_project_access(task.project_id, current_user_id, session)

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    _verify_project_access(task.project_id, current_user_id, session)
    session.delete(task)
    session.commit()
