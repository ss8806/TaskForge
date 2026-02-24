from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from app.core.security import decode_access_token
from app.db.session import get_session
from app.models import User

# Reexport for convenience
SessionDep = Annotated[Session, Depends(get_session)]

_bearer_scheme = HTTPBearer()


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> int:
    """
    JWTトークンを検証し、user_idを返す。
    DBへの問い合わせは行わない（完全ステートレス設計）。
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = int(payload["sub"])
    return user_id


CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    session: SessionDep,
) -> User:
    """
    JWTトークンを検証し、ユーザーオブジェクトを返す。
    管理者権限チェックなどに使用する。
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = int(payload["sub"])
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    # JWTペイロードからロール情報を設定（DBのロールと一致することを確認）
    user.role = payload.get("role", "user")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUserDep) -> User:
    """
    管理者権限チェック用の依存関係。
    ユーザーが管理者でない場合は403エラーを返す。
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


AdminDep = Annotated[User, Depends(require_admin)]
