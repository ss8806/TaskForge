"""AI APIのテスト。"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.security import hash_password
from app.models import Project, User


def _create_project_for_auth_user(session: Session) -> Project:
    """auth_headers フィクスチャのユーザーに紐づくプロジェクトを作成するヘルパー。"""
    user = session.exec(
        select(User).where(User.email == "auth-test@example.com")
    ).first()
    project = Project(name="AI Test Project", owner_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@patch("app.api.routers.ai.decompose_tasks_async")
def test_start_decomposition(
    mock_decompose: MagicMock,
    client: TestClient,
    auth_headers: dict,
    session: Session,
):
    """AIタスク分解ジョブ開始テスト"""
    project = _create_project_for_auth_user(session)

    # Celeryタスクのモック
    mock_task = MagicMock()
    mock_task.id = "test-job-id-123"
    mock_decompose.delay.return_value = mock_task

    response = client.post(
        f"/api/projects/{project.id}/ai/decompose",
        json={"prompt": "ユーザー認証機能を実装してください"},
        headers=auth_headers,
    )

    assert response.status_code == 202
    data = response.json()
    assert data["job_id"] == "test-job-id-123"
    assert data["status"] == "queued"
    assert "message" in data

    # Celeryタスクが正しい引数で呼ばれたことを検証
    mock_decompose.delay.assert_called_once_with(
        project_id=project.id,
        user_requirement="ユーザー認証機能を実装してください",
        sprint_id=None,
    )


@patch("app.api.routers.ai.decompose_tasks_async")
def test_start_decomposition_with_sprint_id(
    mock_decompose: MagicMock,
    client: TestClient,
    auth_headers: dict,
    session: Session,
):
    """スプリントID指定でのAIタスク分解ジョブ開始テスト"""
    project = _create_project_for_auth_user(session)

    mock_task = MagicMock()
    mock_task.id = "test-job-id-456"
    mock_decompose.delay.return_value = mock_task

    response = client.post(
        f"/api/projects/{project.id}/ai/decompose",
        json={"prompt": "タスク分解", "sprint_id": 42},
        headers=auth_headers,
    )

    assert response.status_code == 202
    mock_decompose.delay.assert_called_once_with(
        project_id=project.id,
        user_requirement="タスク分解",
        sprint_id=42,
    )


def test_start_decomposition_unauthorized(client: TestClient):
    """未認証でのAIタスク分解は失敗"""
    response = client.post(
        "/api/projects/1/ai/decompose",
        json={"prompt": "テスト"},
    )

    assert response.status_code in (401, 403)


@patch("app.api.routers.ai.decompose_tasks_async")
def test_start_decomposition_forbidden_project(
    mock_decompose: MagicMock,
    client: TestClient,
    auth_headers: dict,
    session: Session,
):
    """他ユーザーのプロジェクトでのAIタスク分解は拒否"""
    other_user = User(
        email="other-ai@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    other_project = Project(name="Other AI Project", owner_id=other_user.id)
    session.add(other_project)
    session.commit()
    session.refresh(other_project)

    response = client.post(
        f"/api/projects/{other_project.id}/ai/decompose",
        json={"prompt": "テスト"},
        headers=auth_headers,
    )

    assert response.status_code == 403
    # Celeryタスクが呼ばれていないことを検証
    mock_decompose.delay.assert_not_called()


def test_start_decomposition_project_not_found(
    client: TestClient,
    auth_headers: dict,
):
    """存在しないプロジェクトでのAIタスク分解は404"""
    response = client.post(
        "/api/projects/99999/ai/decompose",
        json={"prompt": "テスト"},
        headers=auth_headers,
    )

    assert response.status_code == 404


@patch("app.api.routers.ai.get_task_status")
def test_get_decomposition_status_pending(
    mock_get_status: MagicMock,
    client: TestClient,
    auth_headers: dict,
):
    """AIジョブステータス取得: PENDING"""
    mock_get_status.return_value = {
        "status": "PENDING",
        "message": "タスクがキューに入っています",
    }

    response = client.get(
        "/api/ai/jobs/test-job-id-123",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-id-123"
    assert data["status"] == "PENDING"
    assert "message" in data


@patch("app.api.routers.ai.get_task_status")
def test_get_decomposition_status_completed(
    mock_get_status: MagicMock,
    client: TestClient,
    auth_headers: dict,
):
    """AIジョブステータス取得: 完了"""
    mock_get_status.return_value = {
        "status": "SUCCESS",
        "message": "タスクが完了しました",
        "result": {"tasks_count": 5, "sprints_count": 2},
    }

    response = client.get(
        "/api/ai/jobs/test-job-completed",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["result"]["tasks_count"] == 5


@patch("app.api.routers.ai.get_task_status")
def test_get_decomposition_status_failed(
    mock_get_status: MagicMock,
    client: TestClient,
    auth_headers: dict,
):
    """AIジョブステータス取得: 失敗"""
    mock_get_status.return_value = {
        "status": "FAILURE",
        "message": "タスクが失敗しました",
    }

    response = client.get(
        "/api/ai/jobs/test-job-failed",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILURE"


def test_get_decomposition_status_unauthorized(client: TestClient):
    """未認証でのAIジョブステータス取得は失敗"""
    response = client.get("/api/ai/jobs/test-job-id")

    assert response.status_code in (401, 403)
