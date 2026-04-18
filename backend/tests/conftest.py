import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.session import get_session
from app.main import app
from app.models import User
from tests.factories import (
    ProjectFactory,
    SprintFactory,
    TaskFactory,
    UserFactory,
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # ファクトリにセッションを設定
        UserFactory._meta.sqlalchemy_session = session
        ProjectFactory._meta.sqlalchemy_session = session
        SprintFactory._meta.sqlalchemy_session = session
        TaskFactory._meta.sqlalchemy_session = session
        yield session
        # テスト終了後にセッションをクリア
        UserFactory._meta.sqlalchemy_session = None
        ProjectFactory._meta.sqlalchemy_session = None
        SprintFactory._meta.sqlalchemy_session = None
        TaskFactory._meta.sqlalchemy_session = None


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
    return UserFactory(email="testuser@example.com")


@pytest.fixture
def admin_user(session: Session) -> User:
    """管理者ユーザーフィクスチャ。"""
    return UserFactory(email="admin@example.com", role="admin")


def _make_auth_headers(user: User) -> dict:
    """ユーザーから認証ヘッダーを直接生成するヘルパー。レート制限を回避する。"""
    token = create_access_token(subject=user.id, email=user.email, role=user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client: TestClient, session: Session) -> dict:
    """認証済みリクエスト用ヘッダーフィクスチャ。"""
    user = User(
        email="auth-test@example.com",
        password_hash=hash_password("testpassword123"),
        role="user",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return _make_auth_headers(user)


@pytest.fixture
def admin_auth_headers(client: TestClient, session: Session) -> dict:
    """管理者認証済みリクエスト用ヘッダーフィクスチャ。"""
    admin = User(
        email="admin-test@example.com",
        password_hash=hash_password("testpassword123"),
        role="admin",
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)

    return _make_auth_headers(admin)
