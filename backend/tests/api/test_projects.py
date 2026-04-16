"""プロジェクトAPIのテスト。"""
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import User, Project
from tests.fixtures.auth import create_test_user, get_auth_headers


def test_list_projects(client: TestClient, session: Session):
    """プロジェクト一覧取得のテスト。"""
    user = create_test_user(session)
    headers = get_auth_headers(client, user)

    # プロジェクト作成
    project1 = Project(name="Project 1", owner_id=user.id)
    project2 = Project(name="Project 2", owner_id=user.id)
    session.add(project1)
    session.add(project2)
    session.commit()

    # プロジェクト一覧取得
    response = client.get("/api/projects", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Project 1"
    assert data[1]["name"] == "Project 2"


def test_list_projects_only_own(client: TestClient, session: Session):
    """自分のプロジェクトのみ取得できるテスト。"""
    user1 = create_test_user(session, "user1@example.com")
    user2 = create_test_user(session, "user2@example.com")

    headers1 = get_auth_headers(client, user1)
    headers2 = get_auth_headers(client, user2)

    # user1のプロジェクト作成
    project = Project(name="User1 Project", owner_id=user1.id)
    session.add(project)
    session.commit()

    # user1が自分のプロジェクトのみ取得できる
    response1 = client.get("/api/projects", headers=headers1)
    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1) == 1

    # user2が自分のプロジェクトのみ取得できる（user1のプロジェクトは含まれない）
    response2 = client.get("/api/projects", headers=headers2)
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2) == 0


def test_create_project(client: TestClient, session: Session):
    """プロジェクト作成のテスト。"""
    user = create_test_user(session)
    headers = get_auth_headers(client, user)

    response = client.post(
        "/api/projects",
        headers=headers,
        json={
            "name": "Test Project",
            "description": "A test project"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project"
    assert data["owner_id"] == user.id


def test_create_project_unauthorized(client: TestClient, session: Session):
    """未認証でプロジェクト作成が失敗するテスト。"""
    response = client.post(
        "/api/projects",
        json={
            "name": "Unauthorized Project",
            "description": "This should fail"
        }
    )
    assert response.status_code == 401  # 未認証


def test_get_project(client: TestClient, session: Session):
    """プロジェクト詳細取得のテスト。"""
    user = create_test_user(session)
    headers = get_auth_headers(client, user)

    project = Project(name="Test Project", description="Test Description", owner_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    response = client.get(f"/api/projects/{project.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project.id
    assert data["name"] == "Test Project"
    assert data["description"] == "Test Description"


def test_get_project_unauthorized(client: TestClient, session: Session):
    """他人のプロジェクト詳細取得が失敗するテスト。"""
    user1 = create_test_user(session, "user1@example.com")
    user2 = create_test_user(session, "user2@example.com")

    headers1 = get_auth_headers(client, user1)
    headers2 = get_auth_headers(client, user2)

    # user1のプロジェクト作成
    project = Project(name="User1 Project", owner_id=user1.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    # user2がuser1のプロジェクト詳細を取得しようとする
    response = client.get(f"/api/projects/{project.id}", headers=headers2)
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized"


def test_get_project_not_found(client: TestClient, session: Session):
    """存在しないプロジェクト取得のテスト。"""
    user = create_test_user(session)
    headers = get_auth_headers(client, user)

    response = client.get("/api/projects/99999", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Project not found"


def test_delete_project(client: TestClient, session: Session):
    """プロジェクト削除のテスト。"""
    user = create_test_user(session)
    headers = get_auth_headers(client, user)

    project = Project(name="Project to Delete", owner_id=user.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    # 削除前
    response_before = client.get(f"/api/projects/{project.id}", headers=headers)
    assert response_before.status_code == 200

    # プロジェクト削除
    response = client.delete(f"/api/projects/{project.id}", headers=headers)
    assert response.status_code == 204

    # 削除後
    response_after = client.get(f"/api/projects/{project.id}", headers=headers)
    assert response_after.status_code == 404


def test_delete_project_unauthorized(client: TestClient, session: Session):
    """他人のプロジェクト削除が失敗するテスト。"""
    user1 = create_test_user(session, "user1@example.com")
    user2 = create_test_user(session, "user2@example.com")

    headers1 = get_auth_headers(client, user1)
    headers2 = get_auth_headers(client, user2)

    # user1のプロジェクト作成
    project = Project(name="User1 Project", owner_id=user1.id)
    session.add(project)
    session.commit()
    session.refresh(project)

    # user2がuser1のプロジェクトを削除しようとする
    response = client.delete(f"/api/projects/{project.id}", headers=headers2)
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized"

    # プロジェクトが削除されていないことを確認
    response = client.get(f"/api/projects/{project.id}", headers=headers1)
    assert response.status_code == 200
