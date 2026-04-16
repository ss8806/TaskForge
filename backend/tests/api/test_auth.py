"""認証APIのテスト。"""
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import create_access_token, verify_password, hash_password


def test_register(client: TestClient, session: Session):
    """ユーザー登録のテスト。"""
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client: TestClient, session: Session):
    """重複メールアドレスでの登録失敗テスト。"""
    # 最初のユーザー登録
    client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    # 重複登録
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "testpassword456"}
    )
    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Email already registered"


def test_register_invalid_email(client: TestClient):
    """無効なメールアドレスでの登録失敗テスト。"""
    response = client.post(
        "/api/auth/register",
        json={"email": "invalid-email", "password": "testpassword123"}
    )
    assert response.status_code == 422


def test_login_success(client: TestClient, session: Session):
    """正常なログインのテスト。"""
    # ユーザー作成
    from app.models import User
    from app.core.security import hash_password

    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        role="user"
    )
    session.add(user)
    session.commit()

    # ログイン
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_email(client: TestClient):
    """無効なメールアドレスでのログイン失敗テスト。"""
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 401


def test_login_invalid_password(client: TestClient, session: Session):
    """無効なパスワードでのログイン失敗テスト。"""
    # ユーザー作成
    from app.models import User
    from app.core.security import hash_password

    user = User(
        email="test@example.com",
        password_hash=hash_password("correctpassword"),
        role="user"
    )
    session.add(user)
    session.commit()

    # 間違ったパスワードでログイン
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_password_hashing():
    """パスワードハッシュ機能のテスト。"""
    password = "testpassword123"
    hashed = hash_password(password)

    # ハッシュは元のパスワードと異なる
    assert hashed != password
    # bcrypt形式（$2b$で始まる）
    assert hashed.startswith("$2b$")
    # ハッシュは一貫していない
    hashed2 = hash_password(password)
    assert hashed != hashed2


def test_password_verification():
    """パスワード検証機能のテスト。"""
    password = "testpassword123"
    hashed = hash_password(password)

    # 正しいパスワードで検証
    assert verify_password(password, hashed) is True
    # 間違ったパスワードで検証
    assert verify_password("wrongpassword", hashed) is False


def test_token_creation():
    """トークン作成機能のテスト。"""
    token = create_access_token(subject=1, email="test@example.com", role="user")

    # トークンが文字列である
    assert isinstance(token, str)
    # トークンが空ではない
    assert len(token) > 0


def test_token_decoding():
    """トークンデコード機能のテスト。"""
    from app.core.security import decode_access_token

    user_id = 1
    email = "test@example.com"
    role = "user"

    token = create_access_token(subject=user_id, email=email, role=role)
    decoded = decode_access_token(token)

    assert decoded is not None
    assert decoded["sub"] == str(user_id)
    assert decoded["email"] == email
    assert decoded["role"] == role
    assert "exp" in decoded  # 有効期限が含まれる
