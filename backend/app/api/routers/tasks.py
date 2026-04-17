from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.dependencies import CurrentUserDep, SessionDep, verify_project_access
from app.api.schemas import TaskCreate, TaskResponse, TaskUpdate
from app.models import Task
from app.utils.soft_delete import soft_delete, filter_active

router = APIRouter(tags=["tasks"])


# ── プロジェクト配下のタスクCRUD ─────────────────────────────────────────────


@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
def list_tasks(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
    limit: int = 100,
    offset: int = 0,
    status: str | None = None,
    sprint_id: int | None = None,
):
    verify_project_access(project_id, current_user, session)
    query = select(Task).where(Task.project_id == project_id)
    # ソフトデリートされたタスクを除外
    query = filter_active(query, Task)
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
    current_user: CurrentUserDep,
):
    """タスク作成"""
    verify_project_access(project_id, current_user, session)
    task = Task(project_id=project_id, **body.model_dump())
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
    except Exception:
        session.rollback()
        raise
    return task


# ── 個別タスク操作 ────────────────────────────────────────────────────────────


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    body: TaskUpdate,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """タスク更新"""
    task = session.get(Task, task_id)
    if not task or task.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    verify_project_access(task.project_id, current_user, session)

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    task.updated_at = datetime.now(timezone.utc)

    try:
        session.add(task)
        session.commit()
        session.refresh(task)
    except Exception:
        session.rollback()
        raise
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """タスク削除（ソフトデリート）"""
    task = session.get(Task, task_id)
    if not task or task.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    verify_project_access(task.project_id, current_user, session)
    try:
        # ソフトデリートを実行
        soft_delete(session, task)
    except Exception:
        session.rollback()
        raise
