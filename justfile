# TaskForge 開発コマンド
# https://github.com/casey/just

default:
  just --list

dev:
  @echo "🚀 TaskForge 開発サーバーを起動します..."
  just infra-start
  @echo "⏳ インフラの起動を待機中..."
  @sleep 3
  @echo ""
  @echo "✅ インフラの起動が完了しました。"
  @echo ""
  @echo "💡 以下のコマンドでサーバーを起動してください："
  @echo " ターミナル1: just backend"
  @echo " ターミナル2: just frontend"
  @echo ""
  @echo "⚠️  または、dev-all コマンドで一度に起動できます："
  @echo " just dev-all"

dev-all:
  @echo "🚀 TaskForge を起動します..."
  just infra-start
  @echo "⏳ インフラの起動を待機中..."
  @sleep 3
  @echo ""
  @echo "✅ インフラの起動が完了しました。"
  @echo ""
  ./scripts/dev-all.sh

infra-start:
  @echo "🐳 インフラ（PostgreSQL + Redis）を起動中..."
  docker compose up -d

infra-stop:
  @echo "🛑 インフラを停止中..."
  docker compose down

infra-restart:
  @echo "🔄 インフラを再起動中..."
  docker compose restart

infra-logs:
  docker compose logs -f

backend:
  @echo "🐍 バックエンドを起動中..."
  cd backend && uv run uvicorn app.main:app --reload --port 8000

frontend:
  @echo "⚛️ フロントエンドを起動中..."
  cd frontend && bun run dev

db-migrate:
  @echo "📦 データベースマイグレーションを実行中..."
  cd backend && uv run alembic upgrade head

db-migration message:
  @echo "📝 新しいマイグレーションファイルを作成中..."
  cd backend && uv run alembic revision --autogenerate -m "$message"

db-rollback:
  @echo "⏪ データベースを1つ前の状態に戻す..."
  cd backend && uv run alembic downgrade -1

test:
  just test-backend
  just test-frontend

test-backend:
  @echo "🧪 バックエンドテストを実行中..."
  cd backend && uv run pytest -v

test-frontend:
  @echo "🧪 フロントエンドテストを実行中..."
  cd frontend && bun run test

test-backend-coverage:
  @echo "📊 バックエンドテスト（カバレッジ）を実行中..."
  cd backend && uv run pytest --cov=app --cov-report=html

test-frontend-coverage:
  @echo "📊 フロントエンドテスト（カバレッジ）を実行中..."
  cd frontend && bun run test:coverage

setup:
  @echo "🔧 TaskForgeの初期セットアップを実行中..."
  just infra-start
  just db-migrate
  cd frontend && bun install
  cd backend && uv sync
  @echo "✅ セットアップ完了！ just dev で開発サーバーを起動してください。"

lint:
  just lint-backend
  just lint-frontend

lint-backend:
  @echo "🔍 バックエンドのリンターを実行中..."
  cd backend && uv run ruff check .
  cd backend && uv run mypy .

lint-frontend:
  @echo "🔍 フロントエンドのリンターを実行中..."
  cd frontend && bun run lint

format:
  just format-backend
  just format-frontend

format-backend:
  @echo "✨ バックエンドのコードをフォーマット中..."
  cd backend && uv run ruff format .

format-frontend:
  @echo "✨ フロントエンドのコードをフォーマット中..."
  cd frontend && bun run format

health:
  @echo "🏥 ヘルスチェックを実行中..."
  @curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ バックエンドが応答しません"
  @curl -s http://localhost:3000 | head -1 || echo "❌ フロントエンドが応答しません"
