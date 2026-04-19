#!/bin/bash
# TaskForge 開発サーバー同時起動スクリプト

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🐍 バックエンドを起動中..."
cd "$PROJECT_DIR/backend" && uv run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "🔄 Celeryワーカーを起動中..."
cd "$PROJECT_DIR/backend" && uv run celery -A app.celery_app worker --loglevel=info --concurrency=2 &
CELERY_PID=$!

echo "⚛️ フロントエンドを起動中..."
cd "$PROJECT_DIR/frontend" && npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ バックエンド (PID: $BACKEND_PID)、Celery (PID: $CELERY_PID)、フロントエンド (PID: $FRONTEND_PID) を起動しました"
echo "💡 Ctrl+C で終了できます"
echo ""

# どれかが終了したら全部終了
trap "kill $BACKEND_PID $CELERY_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM EXIT

wait $BACKEND_PID $CELERY_PID $FRONTEND_PID
