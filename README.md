# TaskForge 🚀

AI搭載のインテリジェント・プロジェクト管理アプリケーション。
要件の自然言語入力からタスク分解、スケジュール提案までをAIがサポートします。

## 🏗️ システムアーキテクチャ

- **フロントエンド**: Next.js (App Router), Tailwind CSS, shadcn/ui, TanStack Query
- **バックエンド**: FastAPI, SQLModel (Pydantic + SQLAlchemy)
- **インフラ**: PostgreSQL, Redis, Docker Compose
- **AI**: LangChain/LangGraph + OpenAI API

---

## 🏆️ ポイントシステム

このプロジェクトでは、ポイントと実績システムを使用してエンゲージメントを高めます。

### 動作方法
- ユーザーはタスク（コミット、コードレビューなど）を完了するとポイントを獲得します。
- 特定のポイントマイルストーンに達すると実績が解除ロックされます。
- リーダーボードはトップ貢献者を追跡します。

### 実績一覧
- **初回コミット (First Commit)**: 100 ポイント
- **バグハンター (Bug Hunter)**: 50 ポイント
- **レポクリーナー (Repo Cleaner)**: 30 ポイント

### 今後の改善
- リーダーボードAPIエンドポイントを追加
- ビジュアルバッジ（GitHubスタイルのバッジなど）を追加
- ポイントと実績のデータベース移行

プロジェクトを起動するには、インフラ、バックエンド、フロントエンドの3つを順に起動する必要があります。

### 0. 準備

- Docker / Docker Compose
- Python 3.12+ (uv推奨)
- Node.js 20+

### 1. インフラの起動 (PostgreSQL / Redis)

ルートディレクトリで以下を実行します：
```bash
docker compose up -d
```

### 2. バックエンドのセットアップと起動

別ターミナルで `backend` ディレクトリへ移動します：

```bash
cd backend

# 仮想環境の作成と、依存関係のインストール（uvを使用している場合）
uv sync

# マイグレーションの実行
source .venv/bin/activate
alembic upgrade head

# サーバーの起動
uvicorn app.main:app --reload --port 8000
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. フロントエンドのセットアップと起動

別ターミナルで `frontend` ディレクトリへ移動します：

```bash
cd frontend

# 依存関係のインストール
bun install

# 開発サーバーの起動
bun run dev
```
- アプリケーションURL: [http://localhost:3000](http://localhost:3000)

---

## 📁 ディレクトリ構成

- `frontend/`: Next.js アプリケーション
- `backend/`: FastAPI アプリケーション
- `Docs/`: 要件定義・設計ドキュメント
- `docker-compose.yml`: DBおよびRedisの設定

## 🛠️ 開発ツールと効率化

このプロジェクトでは、開発効率とコード品質を向上させるためのツールを導入しています。

### セキュリティ設定

#### GitHub Actions Secrets の設定（初回のみ）

CI/CDでテストを実行するには、GitHub リポジトリの Secrets に以下を設定する必要があります：

1. GitHub リポジトリページ → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** で以下を追加：

| Secret Name | 設定値 | 生成コマンド |
|-------------|--------|-------------|
| `JWT_SECRET_KEY` | 64文字以上のランダム文字列 | `openssl rand -base64 64` |
| `OPENAI_API_KEY` | あなたのOpenAI APIキー | - |

**注意**: これらのSecretはCI環境でのみ使用され、ログには表示されません。

#### 環境変数の設定

```bash
# ルートディレクトリ
cp .env.example .env
# .envファイルをエディタで開き、実際の値を設定

# バックエンド
cd backend
cp .env.example .env
# .envファイルをエディタで開き、実際の値を設定

# 安全なパスワードの生成
openssl rand -base64 32  # データベース用
openssl rand -base64 64  # JWT用
```

**重要**: `.env`ファイルは絶対にGitにコミットしないでください。

### コードフォーマット・リンティング

#### バックエンド (Python)
```bash
cd backend

# コードフォーマット（ruff）
uv run ruff format .

# リントチェックと自動修正
uv run ruff check . --fix

# 型チェック（mypy）
uv run mypy app/
```

#### フロントエンド (TypeScript/React)
```bash
cd frontend

# コードフォーマット（prettier）
bun run format

# フォーマットチェック（変更なし確認）
bun run format:check

# リントチェック
bun run lint

# リント自動修正
bun run lint:fix
```

### テスト実行

#### バックエンド
```bash
cd backend

# 全テスト実行
uv run pytest tests/ -v

# カバレッジレポート付き
uv run pytest tests/ -v --cov=app --cov-report=html

# 特定のテストファイルだけ実行
uv run pytest tests/api/test_auth.py -v

# テスト並列実行（pytest-xdist導入後）
uv run pytest tests/ -n auto
```

#### フロントエンド
```bash
cd frontend

# 全テスト実行
bun run test

# UI付きテスト（ウォッチモード）
bun run test:ui

# カバレッジレポート付き
bun run test:coverage
```

### テストデータ生成（factory-boy）

バックエンドテストで使用するテストデータを自動生成できます：

```python
# backend/tests/factories.py
from tests.factories import UserFactory, ProjectFactory, TaskFactory

# ユーザー作成
user = UserFactory(email="test@example.com", name="Test User")

# プロジェクト作成（所有者も自動作成）
project = ProjectFactory(name="My Project")

# タスク作成（スプリント、プロジェクト、所有者も自動作成）
task = TaskFactory(title="Important Task")
```

### APIモック（MSW - Mock Service Worker）

フロントエンドテストでAPIレスポンスをモック化：

```typescript
// frontend/src/test/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/projects', () => {
    return HttpResponse.json({
      items: [],
      total: 0,
      page: 1,
      page_size: 20
    })
  })
]
```

### pre-commit フック

コミット時に自動的にコードチェックを実行：

```bash
# pre-commitインストール（初回のみ）
cd backend
uv run pre-commit install

# 手動で全ファイルチェック
uv run pre-commit run --all-files

# 特定のフックだけ実行
uv run pre-commit run ruff --all-files
```

コミット時に以下のチェックが自動実行されます：
- ✅ Ruff（リンティング・フォーマット）
- ✅ mypy（型チェック）
- ✅ pytest（テスト実行）

### React Query DevTools

開発者ツールでクエリ状態を可視化：

- ブラウザ右下にReact Queryアイコンが表示されます
- クリックするとDevToolsが開きます
- クエリキャッシュ、ローディング状態、エラーを確認可能

### テストフィクスチャ

#### バックエンド
```python
# conftest.pyで定義済みのフィクスチャ
@pytest.fixture
def user(session: Session) -> User: ...  # 通常ユーザー

@pytest.fixture
def admin_user(session: Session) -> User: ...  # 管理者ユーザー

@pytest.fixture
def auth_headers(client: TestClient, session: Session) -> dict: ...  # 認証ヘッダー
```

使用例：
```python
def test_create_project(client: TestClient, auth_headers: dict):
    response = client.post(
        "/api/projects",
        json={"name": "Test Project"},
        headers=auth_headers
    )
    assert response.status_code == 200
```

---

## 🛠️ 将来の拡張 (Phase 2+)

- [ ] AIによるタスク自動分解機能の実装
- [ ] Celery による非同期タスク処理
- [ ] ガントチャート・スクラムビューの詳細実装
