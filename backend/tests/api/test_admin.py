"""管理者APIのテスト。"""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import hash_password
from app.models import Project, User


def test_list_users(client: TestClient, admin_auth_headers: dict, session: Session):
    """管理者: 全ユーザー一覧を取得"""
    # テスト用ユーザーを追加
    extra_user = User(
        email="extra@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    session.add(extra_user)
    session.commit()

    response = client.get("/api/admin/users", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    # 管理者ユーザー + 追加ユーザーが含まれる
    assert len(data) >= 2
    emails = [u["email"] for u in data]
    assert "admin-test@example.com" in emails
    assert "extra@example.com" in emails


def test_list_users_forbidden_for_normal_user(client: TestClient, auth_headers: dict):
    """一般ユーザーは管理者APIにアクセスできない"""
    response = client.get("/api/admin/users", headers=auth_headers)

    assert response.status_code == 403


def test_list_users_unauthorized(client: TestClient):
    """未認証ユーザーは管理者APIにアクセスできない"""
    response = client.get("/api/admin/users")

    assert response.status_code in (401, 403)


def test_list_all_projects(
    client: TestClient, admin_auth_headers: dict, session: Session
):
    """管理者: 全プロジェクト一覧を取得"""
    # 別ユーザーのプロジェクトも含めて取得できることを検証
    other_user = User(
        email="projowner@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    project = Project(name="Admin Visible Project", owner_id=other_user.id)
    session.add(project)
    session.commit()

    response = client.get("/api/admin/projects", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert any(p["name"] == "Admin Visible Project" for p in data)


def test_list_all_projects_forbidden_for_normal_user(
    client: TestClient, auth_headers: dict
):
    """一般ユーザーは管理者プロジェクト一覧にアクセスできない"""
    response = client.get("/api/admin/projects", headers=auth_headers)

    assert response.status_code == 403


def test_make_user_admin(
    client: TestClient, admin_auth_headers: dict, session: Session
):
    """管理者: ユーザーを管理者に昇格"""
    target_user = User(
        email="promote@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    session.add(target_user)
    session.commit()
    session.refresh(target_user)

    response = client.post(
        f"/api/admin/users/{target_user.id}/make-admin",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "promoted to admin" in data["detail"]

    # DBで確認
    session.refresh(target_user)
    assert target_user.role == "admin"


def test_make_user_admin_not_found(client: TestClient, admin_auth_headers: dict):
    """存在しないユーザーの管理者昇格"""
    response = client.post(
        "/api/admin/users/99999/make-admin", headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "User not found"


def test_make_user_admin_forbidden_for_normal_user(
    client: TestClient, auth_headers: dict, session: Session
):
    """一般ユーザーは管理者昇格できない"""
    target_user = User(
        email="target@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    session.add(target_user)
    session.commit()
    session.refresh(target_user)

    response = client.post(
        f"/api/admin/users/{target_user.id}/make-admin",
        headers=auth_headers,
    )

    assert response.status_code == 403


def test_revoke_user_admin(
    client: TestClient, admin_auth_headers: dict, session: Session
):
    """管理者: ユーザーの管理者権限を剥奪"""
    target_admin = User(
        email="demote@example.com",
        password_hash=hash_password("password123"),
        role="admin",
    )
    session.add(target_admin)
    session.commit()
    session.refresh(target_admin)

    response = client.post(
        f"/api/admin/users/{target_admin.id}/revoke-admin",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "admin privileges revoked" in data["detail"]

    # DBで確認
    session.refresh(target_admin)
    assert target_admin.role == "user"


def test_revoke_own_admin(
    client: TestClient, admin_auth_headers: dict, session: Session
):
    """自分自身の管理者権限は剥奪できない"""
    # admin_auth_headers で認証されている管理者ユーザーを取得
    from sqlmodel import select

    admin_user = session.exec(
        select(User).where(User.email == "admin-test@example.com")
    ).first()

    response = client.post(
        f"/api/admin/users/{admin_user.id}/revoke-admin",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Cannot revoke your own admin privileges"

    # 権限が変わっていないことを確認
    session.refresh(admin_user)
    assert admin_user.role == "admin"


def test_revoke_user_admin_not_found(client: TestClient, admin_auth_headers: dict):
    """存在しないユーザーの管理者権限剥奪"""
    response = client.post(
        "/api/admin/users/99999/revoke-admin", headers=admin_auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "User not found"


def test_revoke_user_admin_forbidden_for_normal_user(
    client: TestClient, auth_headers: dict, session: Session
):
    """一般ユーザーは管理者権限を剥奪できない"""
    target_admin = User(
        email="admin-target@example.com",
        password_hash=hash_password("password123"),
        role="admin",
    )
    session.add(target_admin)
    session.commit()
    session.refresh(target_admin)

    response = client.post(
        f"/api/admin/users/{target_admin.id}/revoke-admin",
        headers=auth_headers,
    )

    assert response.status_code == 403
