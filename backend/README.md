# TaskForge Backend 🧠

FastAPIを利用したTaskForgeのバックエンドAPIです。

## 技術スタック
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Task Queue**: Celery + Redis
- **Package Manager**: uv

## セットアップ

### 1. 環境変数の設定
`.env` ファイルを作成し、必要な設定を記述してください。
```bash
cp .env.example .env # もしあれば
```

### 2. インストール
```bash
uv sync
```

### 3. DBマイグレーション
```bash
source .venv/bin/activate
alembic upgrade head
```

### 4. 実行
```bash
uvicorn app.main:app --reload --port 8000
```

## API エンドポイント
- `GET /health`: ヘルスチェック
- `POST /api/auth/register`: ユーザー登録
- `POST /api/auth/login`: ログイン
- `GET /api/projects`: プロジェクト一覧取得
- `POST /api/projects`: プロジェクト作成
- `GET /api/projects/{id}/tasks`: タスク一覧取得
