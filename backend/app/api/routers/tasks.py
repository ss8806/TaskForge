from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, func

from app.api.dependencies import CurrentUserDep, SessionDep, verify_project_access
from app.api.schemas import TaskCreate, TaskResponse, TaskUpdate, PaginatedResponse
from app.models import Task
from app.utils.soft_delete import soft_delete, filter_active
from app.utils.pagination import create_paginated_response

router = APIRouter(tags=["tasks"])


# ── プロジェクト配下のタスクCRUD ─────────────────────────────────────────────


@router.get("/projects/{project_id}/tasks", response_model=PaginatedResponse[TaskResponse])
def list_tasks(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    sprint_id: int | None = None,
):
    """タスク一覧取得（ページネーション付き）"""
    verify_project_access(project_id, current_user, session)
    
    # ベースクエリ
    base_query = select(Task).where(Task.project_id == project_id)
    base_query = filter_active(base_query, Task)
    
    # フィルターを適用
    if status is not None:
        base_query = base_query.where(Task.status == status)
    if sprint_id is not None:
        base_query = base_query.where(Task.sprint_id == sprint_id)
    
    # 総件数を取得
    count_query = select(func.count()).select_from(base_query.subquery())
    total = session.exec(count_query).one()
    
    # ページネーションを適用
    offset = (page - 1) * page_size
    query = base_query.offset(offset).limit(page_size)
    tasks = session.exec(query).all()
    
    return create_paginated_response(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size
    )


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
