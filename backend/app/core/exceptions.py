"""
カスタム例外クラス
"""
from fastapi import HTTPException, status


class TaskForgeException(Exception):
    """基底例外クラス"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(TaskForgeException):
    """リソースが見つからない場合の例外"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedException(TaskForgeException):
    """認証エラー"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class ForbiddenException(TaskForgeException):
    """権限不足エラー"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ValidationException(TaskForgeException):
    """バリデーションエラー"""
    def __init__(self, message: str = "Validation error"):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class ConflictException(TaskForgeException):
    """リソース競合エラー"""
    def __init__(self, message: str = "Conflict"):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )


class AIProcessingException(TaskForgeException):
    """AI処理エラー"""
    def __init__(self, message: str = "AI processing failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
