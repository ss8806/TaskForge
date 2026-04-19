#!/bin/bash
# OpenAPI仕様書からTypeScript型を自動生成するスクリプト

set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
OUTPUT_FILE="src/types/generated.ts"

echo "🔄 OpenAPI仕様書をダウンロード中... $BACKEND_URL/openapi.json"

# OpenAPI JSONをダウンロード
curl -s "$BACKEND_URL/openapi.json" -o /tmp/openapi.json

if [ ! -f /tmp/openapi.json ]; then
  echo "❌ OpenAPI仕様書のダウンロードに失敗しました"
  echo "💡 バックエンドサーバーが起動しているか確認してください: $BACKEND_URL"
  exit 1
fi

echo "📝 TypeScript型を生成中..."

# openapi-typescriptで型を生成
bunx openapi-typescript /tmp/openapi.json -o "$OUTPUT_FILE"

# 生成されたファイルの先頭にコメントを追加
TEMP_FILE=$(mktemp)
echo "// ═══════════════════════════════════════════════════════════════════════" > "$TEMP_FILE"
echo "// 自動生成された型定義（OpenAPI Specification）" >> "$TEMP_FILE"
echo "// 手動で編集しないでください" >> "$TEMP_FILE"
echo "// 生成コマンド: just generate-types" >> "$TEMP_FILE"
echo "// 生成日時: $(date '+%Y-%m-%d %H:%M:%S')" >> "$TEMP_FILE"
echo "// ═══════════════════════════════════════════════════════════════════════" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"
cat "$OUTPUT_FILE" >> "$TEMP_FILE"
mv "$TEMP_FILE" "$OUTPUT_FILE"

# フォーマット
bunx prettier --write "$OUTPUT_FILE" 2>/dev/null || true

echo "✅ 型生成完了: $OUTPUT_FILE"
echo "📊 生成された行数: $(wc -l < "$OUTPUT_FILE")"

# クリーンアップ
rm -f /tmp/openapi.json
