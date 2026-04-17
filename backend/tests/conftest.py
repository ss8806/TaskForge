import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db.session import get_session
from app.main import app
from app.models import User
from tests.factories import UserFactory


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def user(session: Session) -> User:
    """通常ユーザーフィクスチャ。"""
    return UserFactory(session=session, email="testuser@example.com", name="Test User")


@pytest.fixture
def admin_user(session: Session) -> User:
    """管理者ユーザーフィクスチャ。"""
    return UserFactory(
        session=session, email="admin@example.com", name="Admin User", role="admin"
    )


@pytest.fixture
def auth_headers(client: TestClient, session: Session) -> dict:
    """認証済みリクエスト用ヘッダーフィクスチャ。"""
    UserFactory(
        session=session,
        email="auth-test@example.com",
        name="Auth Test User",
        password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # testpassword123
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "auth-test@example.com", "password": "testpassword123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
