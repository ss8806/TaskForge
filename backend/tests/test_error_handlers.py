"""エラーハンドラーのテスト。"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.error_handlers import register_error_handlers
from app.core.exceptions import TaskForgeException


@pytest.fixture
def app():
    """テスト用FastAPIアプリ"""
    app = FastAPI()
    register_error_handlers(app)
    
    # テスト用エンドポイント
    @app.get("/test/taskforge-error")
    def raise_taskforge_error():
        raise TaskForgeException(
            message="カスタムエラー",
            status_code=400
        )
    
    @app.get("/test/validation-error")
    def raise_validation_error():
        from fastapi.exceptions import RequestValidationError
        raise RequestValidationError([])
    
    @app.get("/test/db-error")
    def raise_db_error():
        raise SQLAlchemyError("Database error")
    
    @app.get("/test/integrity-error")
    def raise_integrity_error():
        raise IntegrityError("stmt", {}, Exception("unique constraint"))
    
    @app.get("/test/generic-error")
    def raise_generic_error():
        from starlette.exceptions import HTTPException as StarletteHTTPException
        raise StarletteHTTPException(status_code=500, detail="Unexpected error")
    
    return app


@pytest.fixture
def client(app: FastAPI):
    """テストクライアント"""
    return TestClient(app)


class TestTaskForgeExceptionHandler:
    """TaskForgeException ハンドラーのテスト"""

    def test_taskforge_exception(self, client: TestClient):
        """カスタム例外のハンドリング"""
        response = client.get("/test/taskforge-error")
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "TaskForgeException"
        assert data["error"]["message"] == "カスタムエラー"
        assert data["error"]["status_code"] == 400


class TestValidationExceptionHandler:
    """バリデーションエラーハンドラーのテスト"""

    def test_validation_error(self, client: TestClient):
        """バリデーションエラーのハンドリング"""
        response = client.get("/test/validation-error")
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "ValidationError"
        assert data["error"]["message"] == "Request validation failed"
        assert "errors" in data["error"]


class TestSQLAlchemyExceptionHandler:
    """データベースエラーハンドラーのテスト"""

    def test_sqlalchemy_error(self, client: TestClient):
        """一般的なデータベースエラー"""
        response = client.get("/test/db-error")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["type"] == "DatabaseError"
        assert data["error"]["message"] == "Database operation failed"
        assert "detail" in data["error"]

    def test_integrity_error(self, client: TestClient):
        """整合性エラー（409 Conflict）"""
        response = client.get("/test/integrity-error")
        
        assert response.status_code == 409
        data = response.json()
        assert data["error"]["type"] == "ConflictError"
        assert data["error"]["message"] == "Resource conflict detected"
        assert "detail" in data["error"]


class TestGenericExceptionHandler:
    """汎用エラーハンドラーのテスト"""

    def test_generic_error(self, client: TestClient):
        """予期せぬエラーのハンドリング"""
        response = client.get("/test/generic-error")
        
        # StarletteのHTTPExceptionは500を返す
        assert response.status_code == 500
