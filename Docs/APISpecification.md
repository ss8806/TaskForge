# TaskForge API仕様書

## 概要

本ドキュメントは、TaskForgeのRESTful APIエンドポイントを網羅的に定義します。

### ベースURL
- 開発環境: `http://localhost:8000`
- 本番環境: `https://api.taskforge.example.com`

### 認証方式
- **Bearer Token (JWT)**
- 認証必須エンドポイント: `Authorization: Bearer <token>` ヘッダーを付与

### 共通レスポンス形式

#### 成功レスポンス
```json
{
  "id": 1,
  "name": "Project Name",
  "created_at": "2026-04-19T10:00:00",
  "updated_at": "2026-04-19T10:00:00"
}
```

#### ページネーションレスポンス
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

#### エラーレスポンス
```json
{
  "detail": "Error message description"
}
```

### HTTPステータスコード

| コード | 説明 | 使用例 |
|--------|------|--------|
| 200 | 成功 | GET, PUT, PATCH |
| 201 | 作成成功 | POST |
| 202 | 受付済み | 非同期処理の開始 |
| 204 | 成功（コンテンツなし） | DELETE |
| 400 | リクエスト不正 | バリデーションエラー |
| 401 | 認証失敗 | トークンなし/無効 |
| 403 | 認可失敗 | 権限なし |
| 404 | リソースなし | 存在しないID |
| 409 | 競合 | 重複データ |
| 422 | バリデーションエラー | スキーマ違反 |
| 429 | レート制限超過 | 短期間での过多リクエスト |
| 500 | サーバーエラー | 内部エラー |

---

## 1. 認証API

### 1.1 ユーザー登録

**エンドポイント**: `POST /api/auth/register`

**リクエスト**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**レスポンス** (201):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**エラー**:
- 409: メールアドレスが既に登録済み
- 422: バリデーションエラー（メール形式、パスワード8文字以上）

---

### 1.2 ログイン

**エンドポイント**: `POST /api/auth/login`

**リクエスト**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**レスポンス** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**エラー**:
- 401: メールアドレスまたはパスワードが間違っている

---

## 2. プロジェクト管理API

### 2.1 プロジェクト一覧取得

**エンドポイント**: `GET /api/projects`

**認証**: 必須

**クエリパラメータ**:
- `page` (int, default: 1): ページ番号
- `page_size` (int, default: 20): 1ページあたりの件数

**レスポンス** (200):
```json
{
  "items": [
    {
      "id": 1,
      "name": "My Project",
      "description": "Project description",
      "owner_id": 1,
      "created_at": "2026-04-19T10:00:00",
      "updated_at": "2026-04-19T10:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

---

### 2.2 プロジェクト作成

**エンドポイント**: `POST /api/projects`

**認証**: 必須

**リクエスト**:
```json
{
  "name": "New Project",
  "description": "Project description (optional)"
}
```

**レスポンス** (201):
```json
{
  "id": 1,
  "name": "New Project",
  "description": "Project description (optional)",
  "owner_id": 1,
  "created_at": "2026-04-19T10:00:00",
  "updated_at": "2026-04-19T10:00:00"
}
```

---

### 2.3 プロジェクト詳細取得

**エンドポイント**: `GET /api/projects/{id}`

**認証**: 必須（オーナーのみ）

**レスポンス** (200):
```json
{
  "id": 1,
  "name": "My Project",
  "description": "Project description",
  "owner_id": 1,
  "created_at": "2026-04-19T10:00:00",
  "updated_at": "2026-04-19T10:00:00"
}
```

**エラー**:
- 403: 他のユーザーのプロジェクトにアクセス
- 404: プロジェクトが存在しない

---

### 2.4 プロジェクト削除

**エンドポイント**: `DELETE /api/projects/{id}`

**認証**: 必須（オーナーのみ）

**レスポンス**: 204（コンテンツなし）

**エラー**:
- 403: 他のユーザーのプロジェクトを削除
- 404: プロジェクトが存在しない

---

## 3. タスク管理API

### 3.1 タスク一覧取得

**エンドポイント**: `GET /api/projects/{project_id}/tasks`

**認証**: 必須

**クエリパラメータ**:
- `page` (int, default: 1): ページ番号
- `page_size` (int, default: 20): 1ページあたりの件数
- `status` (string, optional): ステータスフィルタ (`todo`, `doing`, `done`)
- `sprint_id` (int, optional): スプリントIDフィルタ

**レスポンス** (200):
```json
{
  "items": [
    {
      "id": 1,
      "project_id": 1,
      "sprint_id": null,
      "title": "Implement login feature",
      "description": "Add user authentication",
      "status": "todo",
      "priority": 2,
      "start_date": null,
      "end_date": null,
      "estimate": 8.0,
      "created_at": "2026-04-19T10:00:00",
      "updated_at": "2026-04-19T10:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

---

### 3.2 タスク作成

**エンドポイント**: `POST /api/projects/{project_id}/tasks`

**認証**: 必須

**リクエスト**:
```json
{
  "title": "New Task",
  "description": "Task description",
  "status": "todo",
  "priority": 2,
  "sprint_id": null,
  "start_date": null,
  "end_date": null,
  "estimate": 8.0
}
```

**レスポンス** (201):
```json
{
  "id": 1,
  "project_id": 1,
  "title": "New Task",
  "status": "todo",
  "priority": 2,
  "created_at": "2026-04-19T10:00:00",
  "updated_at": "2026-04-19T10:00:00"
}
```

---

### 3.3 タスク更新

**エンドポイント**: `PUT /api/tasks/{task_id}`

**認証**: 必須

**リクエスト**（一部のみ更新可能）:
```json
{
  "title": "Updated Title",
  "status": "doing",
  "priority": 3
}
```

**許可されるステータス値**: `todo`, `doing`, `done`

**レスポンス** (200): 更新後のタスクオブジェクト

**エラー**:
- 404: タスクが存在しない
- 422: 不正なステータス値

---

### 3.4 タスク削除

**エンドポイント**: `DELETE /api/tasks/{task_id}`

**認証**: 必須

**レスポンス**: 204（コンテンツなし）

**注意**: ソフトデリート実装（`deleted_at` が設定される）

---

## 4. スプリント管理API

### 4.1 スプリント一覧取得

**エンドポイント**: `GET /api/projects/{project_id}/sprints`

**認証**: 必須

**レスポンス** (200):
```json
[
  {
    "id": 1,
    "project_id": 1,
    "name": "Sprint 1",
    "start_date": "2026-04-01T00:00:00",
    "end_date": "2026-04-14T00:00:00",
    "created_at": "2026-04-19T10:00:00",
    "updated_at": "2026-04-19T10:00:00"
  }
]
```

**注意**: ページネーションなし（全件取得）

---

### 4.2 スプリント作成

**エンドポイント**: `POST /api/projects/{project_id}/sprints`

**認証**: 必須

**リクエスト**:
```json
{
  "name": "Sprint 1",
  "start_date": "2026-04-01T00:00:00",
  "end_date": "2026-04-14T00:00:00"
}
```

**レスポンス** (201): 作成されたスプリントオブジェクト

---

### 4.3 スプリント更新

**エンドポイント**: `PUT /api/projects/{project_id}/sprints/{sprint_id}`

**認証**: 必須

**リクエスト**:
```json
{
  "name": "Updated Sprint Name"
}
```

**レスポンス** (200): 更新後のスプリントオブジェクト

---

### 4.4 スプリント削除

**エンドポイント**: `DELETE /api/projects/{project_id}/sprints/{sprint_id}`

**認証**: 必須

**レスポンス**: 204（コンテンツなし）

**注意**: ソフトデリート実装

---

## 5. AI処理API

### 5.1 AIタスク分解開始（非同期）

**エンドポイント**: `POST /api/projects/{project_id}/ai/decompose`

**認証**: 必須

**リクエスト**:
```json
{
  "prompt": "ユーザー認証機能を実装してください",
  "sprint_id": null
}
```

**レスポンス** (202):
```json
{
  "job_id": "abc123-def456",
  "status": "queued",
  "message": "AIタスク分解を開始しました。ジョブIDでステータスを確認してください。"
}
```

---

### 5.2 AIジョブステータス取得

**エンドポイント**: `GET /api/ai/jobs/{job_id}`

**認証**: 必須

**レスポンス** (200):

**処理中**:
```json
{
  "job_id": "abc123-def456",
  "status": "PENDING",
  "message": "タスクがキューに入っています",
  "result": null,
  "meta": null
}
```

**完了**:
```json
{
  "job_id": "abc123-def456",
  "status": "SUCCESS",
  "message": "タスクが完了しました",
  "result": {
    "tasks_count": 5,
    "sprints_count": 2
  },
  "meta": null
}
```

---

## 6. ポイントAPI

### 6.1 自分のポイント取得

**エンドポイント**: `GET /api/points/me`

**認証**: 必須

**レスポンス** (200):
```json
{
  "user_id": 1,
  "total_points": 150,
  "achievements": [],
  "points_history": []
}
```

---

### 6.2 ポイント追加

**エンドポイント**: `POST /api/points/me/add`

**認証**: 必須

**リクエスト**:
```json
{
  "points": 50,
  "reason": "タスク完了",
  "task_id": null
}
```

**レスポンス** (200):
```json
{
  "user_id": 1,
  "total_points": 200,
  "achievements": [],
  "points_history": [
    {
      "id": 1,
      "points": 50,
      "reason": "タスク完了",
      "created_at": "2026-04-19T10:00:00"
    }
  ]
}
```

---

### 6.3 実績一覧取得

**エンドポイント**: `GET /api/points/achievements`

**認証**: 不要

**レスポンス** (200):
```json
[
  {
    "id": 1,
    "key": "first_commit",
    "title": "初回コミット",
    "name": "First Commit",
    "description": "最初のコミット",
    "points": 100,
    "icon": null
  }
]
```

---

### 6.4 リーダーボード取得

**エンドポイント**: `GET /api/points/leaderboard`

**認証**: 不要

**クエリパラメータ**:
- `limit` (int, default: 10): 取得件数

**レスポンス** (200):
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "total_points": 300,
    "rank": 1
  }
]
```

---

## 7. 管理者API

### 7.1 ユーザー一覧取得

**エンドポイント**: `GET /api/admin/users`

**認証**: 必須（adminロール）

**クエリパラメータ**:
- `page` (int, default: 1)
- `page_size` (int, default: 20)

**レスポンス** (200): ページネーション形式のユーザー一覧

---

### 7.2 プロジェクト一覧取得

**エンドポイント**: `GET /api/admin/projects`

**認証**: 必須（adminロール）

**レスポンス** (200): ページネーション形式のプロジェクト一覧

---

### 7.3 実績作成

**エンドポイント**: `POST /api/admin/achievements`

**認証**: 必須（adminロール）

**リクエスト**:
```json
{
  "key": "bug_hunter",
  "title": "バグハンター",
  "name": "Bug Hunter",
  "description": "バグを修正",
  "points": 50,
  "icon": null
}
```

**レスポンス** (201): 作成された実績オブジェクト

---

## 8. ヘルスチェック

### 8.1 ヘルスチェック

**エンドポイント**: `GET /health`

**認証**: 不要

**レスポンス** (200):
```json
{
  "status": "healthy",
  "timestamp": "2026-04-19T10:00:00"
}
```

---

## 付録

### A. タスクステータス

| ステータス | 説明 |
|-----------|------|
| `todo` | 未着手 |
| `doing` | 進行中 |
| `done` | 完了 |

### B. タスク優先度

| 優先度 | 説明 |
|--------|------|
| 0 | 低 |
| 1 | 中 |
| 2 | 高 |
| 3 | 緊急 |

### C. ユーザーロール

| ロール | 説明 |
|--------|------|
| `user` | 一般ユーザー |
| `admin` | 管理者 |

### D. レート制限

| エンドポイント | 制限 |
|---------------|------|
| `/api/auth/register` | 5回/分 |
| `/api/auth/login` | 10回/分 |
| その他 | 100回/分 |

---

## 関連ドキュメント

- [データベース設計書](./DatabaseDesign.md)
- [セキュリティ設計書](./SecurityDesign.md)
- [アーキテクチャ設計書](./DetailedDesign.md)
