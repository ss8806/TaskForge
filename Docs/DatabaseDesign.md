# TaskForge データベース設計書

## 概要

本ドキュメントは、TaskForgeのデータベーススキーマを定義します。PostgreSQL 15を使用し、SQLModel（Pydantic + SQLAlchemy）でモデル化されています。

### 使用技術
- **DBMS**: PostgreSQL 15-alpine
- **ORM**: SQLModel 0.0.22+
- **マイグレーション**: Alembic 1.13+
- **接続プール**: SQLAlchemy Engine

---

## ER図

```mermaid
erDiagram
    User ||--o{ Project : owns
    User ||--o{ UserAchievement : unlocks
    User ||--o{ PointsHistory : earns
    Project ||--o{ Sprint : contains
    Project ||--o{ Task : contains
    Sprint ||--o{ Task : includes
    Achievement ||--o{ UserAchievement : "unlocked by"
    
    User {
        int id PK
        string email UK
        string password_hash
        string role
        int total_points
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    
    Project {
        int id PK
        string name
        string description
        int owner_id FK
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    
    Sprint {
        int id PK
        int project_id FK
        string name
        datetime start_date
        datetime end_date
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    
    Task {
        int id PK
        int project_id FK
        int sprint_id FK
        string title
        string description
        string status
        int priority
        datetime start_date
        datetime end_date
        float estimate
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    
    Achievement {
        int id PK
        string key UK
        string name
        string title
        string description
        int points
        string icon
        datetime created_at
    }
    
    UserAchievement {
        int id PK
        int user_id FK
        int achievement_id FK
        datetime unlocked_at
    }
    
    PointsHistory {
        int id PK
        int user_id FK
        int points
        string reason
        int task_id
        datetime created_at
    }
```

---

## テーブル定義

### 1. user（ユーザー）

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | - | ユーザーID |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | - | メールアドレス |
| `password_hash` | VARCHAR(255) | NOT NULL | - | パスワードハッシュ（bcrypt） |
| `role` | VARCHAR(20) | NOT NULL | `'user'` | ユーザーロール（`user`, `admin`） |
| `total_points` | INTEGER | NOT NULL | `0` | 合計ポイント |
| `created_at` | TIMESTAMP | NOT NULL | `now()` | 作成日時 |
| `updated_at` | TIMESTAMP | NOT NULL | `now()` | 更新日時 |
| `deleted_at` | TIMESTAMP | NULL | `NULL` | 削除日時（ソフトデリート） |

**インデックス**:
- `ix_user_email` (email)
- `ix_user_deleted_at` (deleted_at)

---

### 2. project（プロジェクト）

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | - | プロジェクトID |
| `name` | VARCHAR(100) | NOT NULL | - | プロジェクト名 |
| `description` | TEXT | NULL | `NULL` | プロジェクト説明 |
| `owner_id` | INTEGER | FK → user.id, NOT NULL, CASCADE DELETE | - | オーナーID |
| `created_at` | TIMESTAMP | NOT NULL | `now()` | 作成日時 |
| `updated_at` | TIMESTAMP | NOT NULL | `now()` | 更新日時 |
| `deleted_at` | TIMESTAMP | NULL | `NULL` | 削除日時（ソフトデリート） |

**インデックス**:
- `ix_project_deleted_at` (deleted_at)

**外部キー制約**:
- `owner_id` → `user.id` (ON DELETE CASCADE)

---

### 3. sprint（スプリント）

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | - | スプリントID |
| `project_id` | INTEGER | FK → project.id, NOT NULL, CASCADE DELETE | - | プロジェクトID |
| `name` | VARCHAR(100) | NOT NULL | - | スプリント名 |
| `start_date` | TIMESTAMP | NULL | `NULL` | 開始日 |
| `end_date` | TIMESTAMP | NULL | `NULL` | 終了日 |
| `created_at` | TIMESTAMP | NOT NULL | `now()` | 作成日時 |
| `updated_at` | TIMESTAMP | NOT NULL | `now()` | 更新日時 |
| `deleted_at` | TIMESTAMP | NULL | `NULL` | 削除日時（ソフトデリート） |

**インデックス**:
- `ix_sprint_deleted_at` (deleted_at)

**外部キー制約**:
- `project_id` → `project.id` (ON DELETE CASCADE)

---

### 4. task（タスク）

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | - | タスクID |
| `project_id` | INTEGER | FK → project.id, NOT NULL, CASCADE DELETE | - | プロジェクトID |
| `sprint_id` | INTEGER | FK → sprint.id, NULL | `NULL` | スプリントID（NULL=バックログ） |
| `title` | VARCHAR(255) | NOT NULL | - | タスクタイトル |
| `description` | TEXT | NULL | `NULL` | タスク説明 |
| `status` | VARCHAR(20) | NOT NULL | `'todo'` | ステータス（`todo`, `doing`, `done`） |
| `priority` | INTEGER | NOT NULL | `0` | 優先度（0=低, 1=中, 2=高, 3=緊急） |
| `start_date` | TIMESTAMP | NULL | `NULL` | 開始日 |
| `end_date` | TIMESTAMP | NULL | `NULL` | 期日 |
| `estimate` | FLOAT | NULL | `NULL` | 推定工数（時間） |
| `created_at` | TIMESTAMP | NOT NULL | `now()` | 作成日時 |
| `updated_at` | TIMESTAMP | NOT NULL | `now()` | 更新日時 |
| `deleted_at` | TIMESTAMP | NULL | `NULL` | 削除日時（ソフトデリート） |

**インデックス**:
- `ix_task_deleted_at` (deleted_at)

**外部キー制約**:
- `project_id` → `project.id` (ON DELETE CASCADE)
- `sprint_id` → `sprint.id` (ON DELETE SET NULL)

---

### 5. achievement（実績）

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | - | 実績ID |
| `key` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | - | 実績キー（英数字） |
| `name` | VARCHAR(100) | NOT NULL | - | 実績名（英語） |
| `title` | VARCHAR(100) | NOT NULL | - | 実績タイトル（日本語） |
| `description` | TEXT | NULL | `NULL` | 実績説明 |
| `points` | INTEGER | NOT NULL | `0` | 付与ポイント |
| `icon` | VARCHAR(100) | NULL | `NULL` | アイコン名 |
| `created_at` | TIMESTAMP | NOT NULL | `now()` | 作成日時 |

**インデックス**:
- `ix_achievement_key` (key, UNIQUE)

---

### 6. user_achievement（ユーザー実績）

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | - | ID |
| `user_id` | INTEGER | FK → user.id, NOT NULL, CASCADE DELETE | - | ユーザーID |
| `achievement_id` | INTEGER | FK → achievement.id, NOT NULL, CASCADE DELETE | - | 実績ID |
| `unlocked_at` | TIMESTAMP | NOT NULL | `now()` | 解除日時 |

**外部キー制約**:
- `user_id` → `user.id` (ON DELETE CASCADE)
- `achievement_id` → `achievement.id` (ON DELETE CASCADE)

---

### 7. points_history（ポイント履歴）

| カラム名 | データ型 | 制約 | デフォルト | 説明 |
|---------|---------|------|-----------|------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | - | ID |
| `user_id` | INTEGER | FK → user.id, NOT NULL, CASCADE DELETE | - | ユーザーID |
| `points` | INTEGER | NOT NULL | - | ポイント（正=獲得, 負=減点） |
| `reason` | VARCHAR(255) | NULL | `NULL` | 理由 |
| `task_id` | INTEGER | NULL | `NULL` | 関連タスクID |
| `created_at` | TIMESTAMP | NOT NULL | `now()` | 付与日時 |

**外部キー制約**:
- `user_id` → `user.id` (ON DELETE CASCADE)

---

## リレーションシップ

### 1対多（1:N）

| 親テーブル | 子テーブル | 関係 | 削除ルール |
|-----------|-----------|------|-----------|
| User | Project | 1人のユーザーは複数のプロジェクトを所有 | CASCADE |
| Project | Sprint | 1つのプロジェクトは複数のスプリントを持つ | CASCADE |
| Project | Task | 1つのプロジェクトは複数のタスクを持つ | CASCADE |
| Sprint | Task | 1つのスプリントは複数のタスクを含む | SET NULL |
| User | UserAchievement | 1人のユーザーは複数の実績を持つ | CASCADE |
| User | PointsHistory | 1人のユーザーは複数のポイント履歴を持つ | CASCADE |
| Achievement | UserAchievement | 1つの実績は複数のユーザーに解除される | CASCADE |

---

## ソフトデリート仕様

### 概要

TaskForgeでは、データの物理削除ではなく論理削除（ソフトデリート）を採用しています。これにより：
- データの復元が可能
- 監査証跡を保持
- 参照整合性を維持

### 実装

**deleted_at カラム**:
- `NULL`: アクティブ（削除されていない）
- `TIMESTAMP`: 削除された日時

**ユーティリティ関数** (`app/utils/soft_delete.py`):

```python
def soft_delete(session: Session, item: SQLModel) -> None:
    """ソフトデリートを実行"""
    item.deleted_at = datetime.utcnow()
    session.add(item)
    session.commit()

def filter_active(query: Select, model: SQLModel) -> Select:
    """アクティブなレコードのみをフィルタ"""
    return query.where(model.deleted_at == None)

def restore_item(session: Session, item: SQLModel) -> None:
    """削除されたレコードを復元"""
    item.deleted_at = None
    session.add(item)
    session.commit()
```

### 対象テーブル

- `user`
- `project`
- `sprint`
- `task`

**注意**: `achievement`, `user_achievement`, `points_history` はソフトデリートを実装していません。

---

## マイグレーション管理

### Alembic 設定

**設定ファイル**: `backend/alembic.ini`

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:password@localhost:5432/taskforge
```

### マイグレーション履歴

| リビジョン | 日付 | 説明 |
|-----------|------|------|
| `a986506088ad` | 2026-04-xx | 初期スキーマ（user, project, sprint, task） |
| `834d79f0b33c` | 2026-04-xx | project.description カラム追加 |
| `ef5b857ce607` | 2026-04-xx | user.role カラム追加 |
| `60aabd7adfb5` | 2026-04-xx | ソフトデリートカラム追加 |
| `88e5fcd2b3a5` | 2026-04-xx | ポイントシステムテーブル追加 |
| `1e22211c0b09` | 2026-04-19 | achievement.key, achievement.title カラム追加 |

### 使用方法

```bash
# マイグレーション適用
uv run alembic upgrade head

# 新しいマイグレーション作成
uv run alembic revision --autogenerate -m "description"

# 1つ前のバージョンに戻す
uv run alembic downgrade -1
```

---

## インデックス戦略

### 主要インデックス

| テーブル | カラム | 種類 | 目的 |
|---------|--------|------|------|
| user | email | UNIQUE | ログイン検索 |
| user | deleted_at | BTREE | ソフトデリートフィルタ |
| achievement | key | UNIQUE | 実績キー検索 |
| project | deleted_at | BTREE | ソフトデリートフィルタ |
| sprint | deleted_at | BTREE | ソフトデリートフィルタ |
| task | deleted_at | BTREE | ソフトデリートフィルタ |

### 外部キーインデックス

PostgreSQLは外部キーに自動でインデックスを作成しません。必要に応じて追加します：

```sql
-- 例: task.project_id のインデックス
CREATE INDEX ix_task_project_id ON task (project_id);

-- 例: task.sprint_id のインデックス
CREATE INDEX ix_task_sprint_id ON task (sprint_id);
```

---

## パフォーマンス考慮事項

### クエリ最適化

1. **ページネーション**: OFFSET/LIMIT よりカーソルベースを優先（大量データ）
2. **インデックス活用**: WHERE句、JOIN句、ORDER BY句でインデックスを活用
3. **N+1問題防止**: Relationshipで `lazy="select"` を適切に設定

### 接続プール

```python
from sqlmodel import create_engine

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,          # 最大接続数
    max_overflow=10,       # オーバーフロー接続数
    pool_pre_ping=True,    # 接続チェック
    pool_recycle=3600,     # 接続再利用時間（秒）
)
```

---

## セキュリティ

### パスワード管理

- **ハッシュアルゴリズム**: bcrypt
- **ソルト**: 自動生成
- **ストレージ**: `password_hash` カラム

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)
```

### SQLインジェクション対策

- SQLModelのパラメータ化クエリを使用
- 生SQLクエリは使用しない

```python
# ✅ 安全
statement = select(User).where(User.email == email)
users = session.exec(statement).all()

# ❌ 危険
cursor.execute(f"SELECT * FROM user WHERE email = '{email}'")
```

---

## 関連ドキュメント

- [API仕様書](./APISpecification.md)
- [セキュリティ設計書](./SecurityDesign.md)
- [アーキテクチャ設計書](./DetailedDesign.md)
- [repowiki データベース設計](../.qoder/repowiki/ja/content/データベース設計/データベース設計.md)
