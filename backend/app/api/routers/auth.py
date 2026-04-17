from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import select

from app.api.dependencies import SessionDep
from app.api.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
def register(request: Request, body: RegisterRequest, session: SessionDep):
    """ユーザー登録エンドポイント（レート制限：5回/分）"""
    # 重複チェック
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(email=body.email, password_hash=hash_password(body.password))
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception:
        session.rollback()
        raise
    # user.id is guaranteed to be int after commit and refresh
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User ID is None"
        )
    token = create_access_token(subject=user.id, email=user.email, role=user.role)  # type: ignore
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, body: LoginRequest, session: SessionDep):
    """ユーザーログインエンドポイント（レート制限：10回/分）"""
    # ユーザー検索
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # パスワード検証
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWTトークン生成
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User ID is None",
        )

    token = create_access_token(subject=user.id, email=user.email, role=user.role)
    return TokenResponse(access_token=token)
