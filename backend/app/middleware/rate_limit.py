"""Rate limiting middleware for API endpoints."""
from fastapi import Request, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# レート制限の設定
# デフォルト: 1分あたり10回のリクエストを許可
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10/minute"],
    storage_uri="memory://"
)


def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """レート制限超過時のハンドラー"""
    return {
        "detail": f"レート制限を超過しました: {exc.detail}",
        "status": status.HTTP_429_TOO_MANY_REQUESTS
    }
