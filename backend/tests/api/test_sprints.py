"""スプリントAPIのテスト。"""

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.security import hash_password
from app.models import Project, Sprint, User


def _create_project_for_auth_user(session: Session) -> Project:
    """auth_headers フィクスチャのユーザーに紐づくプロジェクトを作成するヘルパー。"""
    user = session.exec(
        select(User).where(User.email == "auth-test@example.com")
    ).first()
    project = Project(name="Sprint Test Project", owner_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def test_create_sprint(client: TestClient, auth_headers: dict, session: Session):
    """スプリント作成テスト"""
    project = _create_project_for_auth_user(session)

    response = client.post(
        f"/api/projects/{project.id}/sprints",
        json={"name": "Sprint 1"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sprint 1"
    assert data["project_id"] == project.id


def test_create_sprint_with_dates(
    client: TestClient, auth_headers: dict, session: Session
):
    """日付付きスプリント作成テスト"""
    project = _create_project_for_auth_user(session)

    response = client.post(
        f"/api/projects/{project.id}/sprints",
        json={
            "name": "Sprint with Dates",
            "start_date": "2026-04-01T00:00:00",
            "end_date": "2026-04-14T00:00:00",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sprint with Dates"
    assert data["start_date"] is not None
    assert data["end_date"] is not None


def test_create_sprint_unauthorized(client: TestClient, session: Session):
    """未認証でのスプリント作成は失敗"""
    response = client.post(
        "/api/projects/1/sprints",
        json={"name": "Sprint 1"},
    )

    assert response.status_code in (401, 403)


def test_create_sprint_forbidden_project(
    client: TestClient, auth_headers: dict, session: Session
):
    """他ユーザーのプロジェクトにスプリント作成は拒否"""
    other_user = User(
        email="other-sprint@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    other_project = Project(name="Other Project", owner_id=other_user.id)
    session.add(other_project)
    session.commit()
    session.refresh(other_project)

    response = client.post(
        f"/api/projects/{other_project.id}/sprints",
        json={"name": "Hacked Sprint"},
        headers=auth_headers,
    )

    assert response.status_code == 403


def test_list_sprints(client: TestClient, auth_headers: dict, session: Session):
    """スプリント一覧取得テスト"""
    project = _create_project_for_auth_user(session)

    # スプリントを作成
    sprint1 = Sprint(name="Sprint A", project_id=project.id)
    sprint2 = Sprint(name="Sprint B", project_id=project.id)
    session.add(sprint1)
    session.add(sprint2)
    session.commit()

    response = client.get(f"/api/projects/{project.id}/sprints", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [s["name"] for s in data]
    assert "Sprint A" in names
    assert "Sprint B" in names


def test_list_sprints_pagination(
    client: TestClient, auth_headers: dict, session: Session
):
    """スプリント一覧のページネーション"""
    project = _create_project_for_auth_user(session)

    for i in range(5):
        session.add(Sprint(name=f"Sprint {i}", project_id=project.id))
    session.commit()

    response = client.get(
        f"/api/projects/{project.id}/sprints?limit=2&offset=0",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2


def test_list_sprints_forbidden_project(
    client: TestClient, auth_headers: dict, session: Session
):
    """他ユーザーのプロジェクトのスプリント一覧は拒否"""
    other_user = User(
        email="other-list-sprint@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    other_project = Project(name="Other Sprint Project", owner_id=other_user.id)
    session.add(other_project)
    session.commit()
    session.refresh(other_project)

    response = client.get(
        f"/api/projects/{other_project.id}/sprints", headers=auth_headers
    )

    assert response.status_code == 403


def test_list_sprints_project_not_found(client: TestClient, auth_headers: dict):
    """存在しないプロジェクトのスプリント一覧"""
    response = client.get("/api/projects/99999/sprints", headers=auth_headers)

    assert response.status_code == 404


def test_update_sprint(client: TestClient, auth_headers: dict, session: Session):
    """スプリント更新テスト"""
    project = _create_project_for_auth_user(session)

    sprint = Sprint(name="Original Sprint", project_id=project.id)
    session.add(sprint)
    session.commit()
    session.refresh(sprint)

    response = client.put(
        f"/api/projects/{project.id}/sprints/{sprint.id}",
        json={"name": "Updated Sprint"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Sprint"


def test_update_sprint_not_found(
    client: TestClient, auth_headers: dict, session: Session
):
    """存在しないスプリントの更新"""
    project = _create_project_for_auth_user(session)

    response = client.put(
        f"/api/projects/{project.id}/sprints/99999",
        json={"name": "Updated"},
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_update_sprint_forbidden_project(
    client: TestClient, auth_headers: dict, session: Session
):
    """他ユーザーのプロジェクトのスプリント更新は拒否"""
    other_user = User(
        email="other-update-sprint@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    other_project = Project(name="Other Update Project", owner_id=other_user.id)
    session.add(other_project)
    session.commit()
    session.refresh(other_project)

    sprint = Sprint(name="Other Sprint", project_id=other_project.id)
    session.add(sprint)
    session.commit()
    session.refresh(sprint)

    response = client.put(
        f"/api/projects/{other_project.id}/sprints/{sprint.id}",
        json={"name": "Hacked"},
        headers=auth_headers,
    )

    assert response.status_code == 403


def test_delete_sprint(client: TestClient, auth_headers: dict, session: Session):
    """スプリント削除テスト"""
    project = _create_project_for_auth_user(session)

    sprint = Sprint(name="Delete Me", project_id=project.id)
    session.add(sprint)
    session.commit()
    session.refresh(sprint)

    response = client.delete(
        f"/api/projects/{project.id}/sprints/{sprint.id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    # 削除確認
    deleted = session.get(Sprint, sprint.id)
    assert deleted is None


def test_delete_sprint_not_found(
    client: TestClient, auth_headers: dict, session: Session
):
    """存在しないスプリントの削除"""
    project = _create_project_for_auth_user(session)

    response = client.delete(
        f"/api/projects/{project.id}/sprints/99999",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_delete_sprint_forbidden_project(
    client: TestClient, auth_headers: dict, session: Session
):
    """他ユーザーのプロジェクトのスプリント削除は拒否"""
    other_user = User(
        email="other-delete-sprint@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    other_project = Project(name="Other Delete Project", owner_id=other_user.id)
    session.add(other_project)
    session.commit()
    session.refresh(other_project)

    sprint = Sprint(name="Other Sprint Delete", project_id=other_project.id)
    session.add(sprint)
    session.commit()
    session.refresh(sprint)

    response = client.delete(
        f"/api/projects/{other_project.id}/sprints/{sprint.id}",
        headers=auth_headers,
    )

    assert response.status_code == 403
