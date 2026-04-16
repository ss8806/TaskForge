"""認証関連のテストフィクスチャとヘルパー関数。"""
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.core.security import create_access_token
from app.models import User


def create_test_user(session: Session, email: str = "test@example.com", password: str = "testpassword123") -> User:
    """テストユーザーを作成するヘルパー関数。"""
    user = User(
        email=email,
        password_hash=password,  # テスト用に簡略化（本番ではハッシュが必要）
        role="user"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_auth_headers(client: TestClient, user: User) -> dict[str, str]:
    """認証ヘッダーを取得するヘルパー関数。"""
    token = create_access_token(subject=user.id, email=user.email, role=user.role)
    return {"Authorization": f"Bearer {token}"}


def login_user(client: TestClient, email: str = "test@example.com", password: str = "testpassword123") -> dict[str, str]:
    """ログインして認証ヘッダーを返すヘルパー関数。"""
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
