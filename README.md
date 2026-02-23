# TaskForge 🚀

AI搭載のインテリジェント・プロジェクト管理アプリケーション。
要件の自然言語入力からタスク分解、スケジュール提案までをAIがサポートします。

## 🏗️ システムアーキテクチャ

- **フロントエンド**: Next.js (App Router), Tailwind CSS, shadcn/ui, TanStack Query
- **バックエンド**: FastAPI, SQLModel (Pydantic + SQLAlchemy)
- **インフラ**: PostgreSQL, Redis, Docker Compose
- **AI**: LangChain/LangGraph + OpenAI API

---

## 🚀 実行手順

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
npm install

# 開発サーバーの起動
npm run dev
```
- アプリケーションURL: [http://localhost:3000](http://localhost:3000)

---

## 📁 ディレクトリ構成

- `frontend/`: Next.js アプリケーション
- `backend/`: FastAPI アプリケーション
- `Docs/`: 要件定義・設計ドキュメント
- `docker-compose.yml`: DBおよびRedisの設定

## 🛠️ 将来の拡張 (Phase 2+)

- [ ] AIによるタスク自動分解機能の実装
- [ ] Celery による非同期タスク処理
- [ ] ガントチャート・スクラムビューの詳細実装
