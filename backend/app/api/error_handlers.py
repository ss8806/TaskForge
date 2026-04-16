"""
グローバル例外ハンドラー
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.exceptions import TaskForgeException


async def taskforge_exception_handler(request: Request, exc: TaskForgeException):
    """カスタム例外ハンドラー"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "status_code": exc.status_code,
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydanticバリデーションエラーハンドラー"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "ValidationError",
                "message": "Request validation failed",
                "errors": errors,
            }
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """データベースエラーハンドラー"""
    error_message = str(exc)
    
    # IntegrityErrorの場合は競合エラーとして扱う
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": {
                    "type": "ConflictError",
                    "message": "Resource conflict detected",
                    "detail": error_message,
                }
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "DatabaseError",
                "message": "Database operation failed",
                "detail": error_message,
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """汎用例外ハンドラー"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred",
            }
        }
    )


def register_error_handlers(app):
    """アプリケーションにエラーハンドラーを登録"""
    app.add_exception_handler(TaskForgeException, taskforge_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
