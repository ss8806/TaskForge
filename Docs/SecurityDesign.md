# TaskForge セキュリティ設計書

## 概要

本ドキュメントは、TaskForgeのセキュリティ対策を包括的に定義します。認証・認可、データ保護、入力検証、レート制限などのセキュリティメカニズムについて詳述します。

---

## 1. 認証システム

### 1.1 JWT認証フロー

#### 概要
TaskForgeではステートレスなJWT（JSON Web Token）認証を採用しています。

**技術スタック**:
- **ライブラリ**: python-jose (JWT), passlib + bcrypt (パスワードハッシュ)
- **アルゴリズム**: HS256
- **トークン有効期限**: 30分（設定可能）

#### トークン生成

```python
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def create_access_token(
    subject: int,
    email: str,
    role: str,
    expires_delta: timedelta | None = None
) -> str:
    """JWTアクセストークンを生成"""
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode = {
        "sub": str(subject),      # ユーザーID
        "email": email,           # メールアドレス
        "role": role,             # ユーザーロール
        "exp": expire,            # 有効期限
        "iat": datetime.utcnow()  # 発行日時
    }
    
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
```

**ペイロード構造**:
```json
{
  "sub": "1",
  "email": "user@example.com",
  "role": "user",
  "exp": 1713520800,
  "iat": 1713519000
}
```

#### トークン検証

```python
from jose import JWTError, jwt
from app.core.config import settings

def decode_access_token(token: str) -> dict | None:
    """JWTトークンを検証・デコード"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
```

#### 認証フロー

```mermaid
sequenceDiagram
    participant Client as クライアント
    participant API as Auth API
    participant Security as Security Module
    participant DB as Database

    Client->>API: POST /api/auth/register
    API->>Security: ハッシュ化パスワード
    Security->>DB: ユーザー作成
    DB-->>API: 作成完了
    API->>Security: JWT生成
    Security-->>API: アクセストークン
    API-->>Client: TokenResponse

    Client->>API: POST /api/auth/login
    API->>DB: ユーザー検索
    DB-->>API: User
    API->>Security: パスワード検証
    Security-->>API: 検証結果
    API->>Security: JWT生成
    Security-->>API: アクセストークン
    API-->>Client: TokenResponse

    Client->>API: GET /api/projects (Bearer Token)
    API->>Security: トークン検証
    Security-->>API: ユーザー情報
    API->>DB: データ取得
    DB-->>API: 結果
    API-->>Client: レスポンス
```

---

### 1.2 パスワード管理

#### ハッシュ化アルゴリズム

- **アルゴリズム**: bcrypt
- **ソルト**: 自動生成（ラウンド数: 12）
- **ライブラリ**: passlib

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """パスワードをハッシュ化"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証"""
    return pwd_context.verify(plain_password, hashed_password)
```

#### パスワードポリシー

| 項目 | 要件 |
|------|------|
| 最小文字数 | 8文字 |
| 大文字 | 必須 |
| 小文字 | 必須 |
| 数字 | 必須 |
| 特殊文字 | 任意 |

**バリデーション** (Pydantic):
```python
from pydantic import BaseModel, EmailStr, field_validator

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
```

---

## 2. 認可システム

### 2.1 アクセス制御

#### プロジェクトレベルの認可

```python
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models import User, Project

def verify_project_access(
    project_id: int,
    current_user: User,
    session: Session
) -> Project:
    """プロジェクトへのアクセス権限を検証"""
    project = session.get(Project, project_id)
    if not project or project.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    return project
```

#### 管理者権限チェック

```python
from app.api.dependencies import CurrentUserDep

def require_admin(current_user: CurrentUserDep) -> User:
    """管理者権限を要求"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

### 2.2 認可マトリクス

| リソース | 操作 | オーナー | 他ユーザー | 管理者 |
|---------|------|---------|-----------|--------|
| Project | 作成 | ✅ | ❌ | ✅ |
| Project | 読み取り | ✅ | ❌ | ✅ |
| Project | 更新 | ✅ | ❌ | ✅ |
| Project | 削除 | ✅ | ❌ | ✅ |
| Task | 作成 | ✅ | ❌ | ✅ |
| Task | 読み取り | ✅ | ❌ | ✅ |
| Task | 更新 | ✅ | ❌ | ✅ |
| Task | 削除 | ✅ | ❌ | ✅ |
| Sprint | 作成 | ✅ | ❌ | ✅ |
| Sprint | 読み取り | ✅ | ❌ | ✅ |
| Sprint | 更新 | ✅ | ❌ | ✅ |
| Sprint | 削除 | ✅ | ❌ | ✅ |
| Achievement | 作成 | ❌ | ❌ | ✅ |
| Achievement | 読み取り | ✅ | ✅ | ✅ |
| User | 一覧取得 | ❌ | ❌ | ✅ |

---

## 3. レート制限

### 3.1 実装

- **ライブラリ**: SlowAPI
- **ストレージ**: インメモリ（本番環境でRedis使用可能）
- **デフォルト制限**: 100リクエスト/分

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# ルートごとの制限
@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, body: RegisterRequest):
    ...

@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest):
    ...
```

### 3.2 レート制限ポリシー

| エンドポイント | 制限 | 理由 |
|---------------|------|------|
| `/api/auth/register` | 5回/分 | 不正登録防止 |
| `/api/auth/login` | 10回/分 | ブルートフォース攻撃防止 |
| `/api/ai/decompose` | 3回/分 | AI APIコスト管理 |
| その他 | 100回/分 | 一般的な制限 |

### 3.3 レート制限超過レスポンス

**HTTP 429 Too Many Requests**:
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

---

## 4. CORS設定

### 4.1 設定

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.2 セキュリティ考慮事項

- **開発環境**: `http://localhost:3000`
- **本番環境**: 特定のドメインのみ許可
- **ワイルドカード使用禁止**: `*` は本番環境で使用しない
- **資格情報**: `allow_credentials=True` でCookie/認証情報送信可能

---

## 5. 入力検証

### 5.1 Pydantic スキーマ

**例: タスク作成**:
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=10000)
    status: str = Field(default="todo")
    priority: int = Field(ge=0, le=3, default=0)
    sprint_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimate: Optional[float] = Field(ge=0, default=None)
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = {"todo", "doing", "done"}
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        return v
```

### 5.2 バリデーションエラーレスポンス

**HTTP 422 Unprocessable Entity**:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters",
      "input": "short"
    }
  ]
}
```

---

## 6. SQLインジェクション対策

### 6.1 SQLModel の使用

```python
# ✅ 安全: パラメータ化クエリ
from sqlmodel import select

def get_user_by_email(email: str, session: Session) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

# ❌ 危険: 生SQLクエリ
def get_user_by_email_unsafe(email: str, session: Session):
    query = f"SELECT * FROM user WHERE email = '{email}'"
    return session.execute(query)
```

### 6.2 対策
- SQLModel ORM を使用（パラメータ化クエリ自動生成）
- 生SQLクエリは使用禁止
- 入力値は必ずPydanticでバリデーション

---

## 7. XSS対策

### 7.1 フロントエンドでの対策

- **React (Next.js)**: デフォルトでJSXがエスケープ
- **dangerouslySetInnerHTML**: 使用禁止（必要な場合はDOMPurifyでサニタイズ）

### 7.2 バックエンドでの対策

- **レスポンスContent-Type**: `application/json`
- **CSPヘッダー**: 本番環境で設定

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["taskforge.example.com"]
)
```

---

## 8. データ保護

### 8.1 ソフトデリート

物理削除ではなく論理削除を採用：

```python
from datetime import datetime

def soft_delete(session: Session, item: SQLModel) -> None:
    """ソフトデリート実行"""
    item.deleted_at = datetime.utcnow()
    session.add(item)
    session.commit()
```

**利点**:
- データ復元可能
- 監査証跡保持
- 参照整合性維持

### 8.2 環境変数管理

**必須環境変数**:
```bash
# .env（Git管理外）
JWT_SECRET_KEY=<64文字以上のランダム文字列>
DATABASE_URL=postgresql://user:pass@localhost:5432/taskforge
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=<OpenAI APIキー>
ALLOWED_ORIGINS=http://localhost:3000
```

**設定ファイル**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str
    REDIS_URL: str
    OPENAI_API_KEY: str
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 9. エラーハンドリング

### 9.1 グローバルエラーハンドラー

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """予期せぬエラーのハンドリング"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP例外のハンドリング"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### 9.2 エラーレスポンス形式

```json
{
  "detail": "Error message"
}
```

**注意**: 本番環境ではスタックトレースをクライアントに返さない

---

## 10. セキュリティチェックリスト

### 10.1 認証・認可

- [ ] JWT_SECRET_KEY が64文字以上のランダム文字列
- [ ] パスワードがbcryptでハッシュ化
- [ ] 有効期限が適切（30分以下）
- [ ] 認証必須エンドポイントに保護
- [ ] 管理者機能にロールチェック
- [ ] プロジェクトオーナー権限の検証

### 10.2 入力検証

- [ ] 全エンドポイントでPydanticスキーマ使用
- [ ] メールアドレス形式の検証
- [ ] パスワード強度の検証
- [ ] 数値範囲の検証（priority, estimate等）
- [ ] 列挙値の検証（status, role等）

### 10.3 データ保護

- [ ] .env が .gitignore に含まれる
- [ ] 機密情報（パスワード、APIキー）をログに出力しない
- [ ] ソフトデリートの実装
- [ ] SQLインジェクション対策（ORM使用）
- [ ] XSS対策（フロントエンドエスケープ）

### 10.4 ネットワーク

- [ ] CORS が適切に設定
- [ ] レート制限が有効
- [ ] 本番環境でHTTPS使用
- [ ] 許可されたホストのみ（TrustedHostMiddleware）

### 10.5 監視・ログ

- [ ] 構造化ログの実装
- [ ] 認証失敗のログ記録
- [ ] 異常アクセスの検知
- [ ] エラーハンドリングの徹底

---

## 11. セキュリティテスト

### 11.1 テストケース

```python
def test_login_invalid_password(client: TestClient):
    """無効なパスワードでログイン失敗"""
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "wrong"}
    )
    assert response.status_code == 401

def test_unauthorized_project_access(client: TestClient):
    """認証なしでプロジェクトアクセス失敗"""
    response = client.get("/api/projects/1")
    assert response.status_code == 401

def test_forbidden_project_access(client: TestClient, auth_headers: dict):
    """他ユーザーのプロジェクトアクセス失敗"""
    response = client.get("/api/projects/999", headers=auth_headers)
    assert response.status_code == 403
```

### 11.2 セキュリティテストツール

- **OWASP ZAP**: Webアプリケーションスキャナー
- **Bandit**: Python セキュリティリンター
- **npm audit**: Node.js 脆弱性チェック

---

## 関連ドキュメント

- [API仕様書](./APISpecification.md)
- [データベース設計書](./DatabaseDesign.md)
- [アーキテクチャ設計書](./DetailedDesign.md)
- [repowiki セキュリティ対策](../.qoder/repowiki/ja/content/セキュリティ対策/セキュリティ対策.md)
- [repowiki JWT認証](../.qoder/repowiki/ja/content/セキュリティ対策/JWT認証.md)
