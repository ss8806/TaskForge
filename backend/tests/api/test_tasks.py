"""
タスクAPIのテスト
"""

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.security import hash_password
from app.models import Project, Task, User


def _get_auth_user(session: Session) -> User:
    """auth_headers フィクスチャで作成されたユーザーを取得するヘルパー。"""
    user = session.exec(
        select(User).where(User.email == "auth-test@example.com")
    ).first()
    return user


def test_create_task(client: TestClient, auth_headers: dict, session: Session):
    """タスク作成テスト"""
    user = _get_auth_user(session)

    project = Project(name="Task Test Project", owner_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    response = client.post(
        f"/api/projects/{project.id}/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": 2,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["project_id"] == project.id
    assert data["status"] == "todo"


def test_list_tasks(client: TestClient, auth_headers: dict, session: Session):
    """タスク一覧取得"""
    user = _get_auth_user(session)

    project = Project(name="List Tasks Project", owner_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    # タスクを作成
    task1 = Task(title="Task 1", project_id=project.id, status="todo")
    task2 = Task(title="Task 2", project_id=project.id, status="in_progress")
    session.add(task1)
    session.add(task2)
    session.commit()

    response = client.get(f"/api/projects/{project.id}/tasks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 2


def test_list_tasks_with_filter(
    client: TestClient, auth_headers: dict, session: Session
):
    """ステータスフィルタリング"""
    user = _get_auth_user(session)

    project = Project(name="Filter Tasks Project", owner_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    # 異なるステータスのタスクを作成
    task_todo = Task(title="Todo Task", project_id=project.id, status="todo")
    task_done = Task(title="Done Task", project_id=project.id, status="done")
    session.add(task_todo)
    session.add(task_done)
    session.commit()

    response = client.get(
        f"/api/projects/{project.id}/tasks?status=todo", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert all(t["status"] == "todo" for t in data["items"])


def test_update_task(client: TestClient, auth_headers: dict, session: Session):
    """タスク更新"""
    user = _get_auth_user(session)

    project = Project(name="Update Task Project", owner_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    task = Task(title="Original Title", project_id=project.id, status="todo")
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.put(
        f"/api/tasks/{task.id}",
        json={"title": "Updated Title", "status": "in_progress"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "in_progress"


def test_update_task_not_found(client: TestClient, auth_headers: dict):
    """存在しないタスク更新"""
    response = client.put(
        "/api/tasks/99999", json={"title": "Updated"}, headers=auth_headers
    )

    assert response.status_code == 404


def test_delete_task(client: TestClient, auth_headers: dict, session: Session):
    """タスク削除"""
    user = _get_auth_user(session)

    project = Project(name="Delete Task Project", owner_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    task = Task(title="Task to Delete", project_id=project.id)
    session.add(task)
    session.commit()
    session.refresh(task)

    response = client.delete(f"/api/tasks/{task.id}", headers=auth_headers)

    assert response.status_code == 204

    # 削除確認
    response = client.get(f"/api/projects/{project.id}/tasks", headers=auth_headers)
    data = response.json()
    assert not any(t["id"] == task.id for t in data["items"])


def test_create_task_forbidden_project(
    client: TestClient, auth_headers: dict, session: Session
):
    """他ユーザーのプロジェクトにタスク作成は拒否"""
    other_user = User(
        email="other_task@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    other_project = Project(name="Other User Project", owner_id=other_user.id)
    session.add(other_project)
    session.commit()
    session.refresh(other_project)

    response = client.post(
        f"/api/projects/{other_project.id}/tasks",
        json={"title": "Hacked Task"},
        headers=auth_headers,
    )

    assert response.status_code == 403
