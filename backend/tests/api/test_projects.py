"""
プロジェクトAPIのテスト
"""

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.security import hash_password
from app.models import Project, User


def _get_auth_user(session: Session) -> User:
    """auth_headers フィクスチャで作成されたユーザーを取得するヘルパー。"""
    user = session.exec(
        select(User).where(User.email == "auth-test@example.com")
    ).first()
    return user


def test_create_project(client: TestClient, auth_headers: dict):
    """プロジェクト作成テスト"""
    response = client.post(
        "/api/projects",
        json={"name": "Test Project", "description": "Test Description"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Test Description"
    assert "id" in data
    assert "owner_id" in data


def test_create_project_without_description(client: TestClient, auth_headers: dict):
    """説明なしでプロジェクト作成"""
    response = client.post(
        "/api/projects", json={"name": "Test Project No Desc"}, headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project No Desc"
    assert data["description"] is None


def test_create_project_unauthorized(client: TestClient):
    """認証なしでプロジェクト作成は失敗"""
    response = client.post("/api/projects", json={"name": "Test Project"})

    assert response.status_code == 401


def test_list_projects(client: TestClient, auth_headers: dict, session: Session):
    """プロジェクト一覧取得"""
    user = _get_auth_user(session)

    project1 = Project(name="Project 1", owner_id=user.id)
    project2 = Project(name="Project 2", owner_id=user.id)
    session.add(project1)
    session.add(project2)
    session.commit()

    response = client.get("/api/projects", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    items = data["items"]
    assert len(items) >= 2
    assert any(p["name"] == "Project 1" for p in items)
    assert any(p["name"] == "Project 2" for p in items)


def test_list_projects_pagination(client: TestClient, auth_headers: dict):
    """ページネーション機能"""
    response = client.get("/api/projects?page=1&page_size=1", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    # PaginatedResponse構造の検証
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert len(data["items"]) <= 1


def test_get_project(client: TestClient, auth_headers: dict, session: Session):
    """プロジェクト詳細取得"""
    user = _get_auth_user(session)

    project = Project(name="Detail Test", owner_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    response = client.get(f"/api/projects/{project.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Detail Test"
    assert data["id"] == project.id


def test_get_project_not_found(client: TestClient, auth_headers: dict):
    """存在しないプロジェクト取得"""
    response = client.get("/api/projects/99999", headers=auth_headers)

    assert response.status_code == 404


def test_get_project_forbidden(
    client: TestClient, auth_headers: dict, session: Session
):
    """他ユーザーのプロジェクトへのアクセス拒否"""
    other_user = User(
        email="other@example.com",
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

    response = client.get(f"/api/projects/{other_project.id}", headers=auth_headers)

    assert response.status_code == 403


def test_delete_project(client: TestClient, auth_headers: dict, session: Session):
    """プロジェクト削除"""
    user = _get_auth_user(session)

    project = Project(name="Delete Test", owner_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    response = client.delete(f"/api/projects/{project.id}", headers=auth_headers)

    assert response.status_code == 204

    # 削除確認
    response = client.get(f"/api/projects/{project.id}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_project_not_found(client: TestClient, auth_headers: dict):
    """存在しないプロジェクト削除"""
    response = client.delete("/api/projects/99999", headers=auth_headers)

    assert response.status_code == 404


def test_delete_project_forbidden(
    client: TestClient, auth_headers: dict, session: Session
):
    """他ユーザーのプロジェクト削除拒否"""
    other_user = User(
        email="other2@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    other_project = Project(name="Other Project 2", owner_id=other_user.id)
    session.add(other_project)
    session.commit()
    session.refresh(other_project)

    response = client.delete(f"/api/projects/{other_project.id}", headers=auth_headers)

    assert response.status_code == 403
