# AI搭載プロジェクト管理アプリ TaskForge 基本設計書

## 1. システム概要
要件定義書（`RequirementsDefinitionDocument.md`）に基づき、タスク管理、プロジェクト管理、AIによるタスク分解機能を備えたポートフォリオ用Webアプリケーション「TaskForge」の基本設計を定義する。

## 2. システムアーキテクチャ
### 2.1 全体構成
フロントエンドとバックエンドを分離したSPA（Single Page Application）構成とし、API経由で通信を行う。

- **Frontend**: Next.js (App Router, TypeScript)
  - ホスティング環境: Node.js
  - スタイリング・UI: Tailwind CSS, shadcn/ui, lucide icons
  - 状態管理、データフェッチ、フォーム、型定義はReact向け標準ライブラリを利用（TanStack Query, React Hook Form, zod等）
- **Admin Frontend**: refine
  - 管理者向けシステム管理・モニタリング画面を提供
- **Backend**: FastAPI (Python)
  - パッケージ管理: uv
  - AI連携モジュール: LangGraph + OpenAI API
  - ORM/バリデーション: SQLModel (Pydantic + SQLAlchemy)
  - 非同期タスクキュー: Celery + Redis
- **Database / Cache**: 
  - メインDB: PostgreSQL (本番環境: GCP Cloud SQL)
  - キャッシュ・メッセージブローカー: Redis (本番環境: GCP Memorystore)
- **インフラ・デプロイ環境 (GCP)**: 
  - フロントエンド・バックエンド・ワーカー: すべてコンテナ化し、**Cloud Run** へデプロイ
  - ローカル開発: Docker Compose によるローカルコンテナ環境展開 (Web, DB, Redis, Celery Worker含む)

### 2.2 システム連携図 (概念)
```text
[User (Browser)]
  │
  ├─(HTTP/REST)─▶ [Frontend (Next.js)]
  │
  └─(HTTP/REST, JWT)─▶ [Backend (FastAPI, SQLModel)] ─(SQL)─▶ [Database (PostgreSQL)]
                               │                       └─(KVS)─▶ [Cache/Broker (Redis)]
                               │                                       │
                               │                                 [Celery Worker]
                               │                                       │
                               └─(API)──────────────────────▶ [OpenAI API (LangGraph)]
```

## 3. 画面・UI設計
UIは3種類のタスクビュー切り替えを主眼とする。

### 3.1 画面一覧
1. **ログイン・サインアップ画面**
   - UI: 認証フォーム（メールアドレス、パスワード）
2. **プロジェクト一覧画面**
   - UI: プロジェクトカード一覧、新規作成ボタン、ログアウトボタン
3. **プロジェクト詳細・タスク管理画面**
   - 上部にビュー切替タブ（カンバン / スクラム / ガントチャート）表示
   - ヘッダー付近に「AIタスク作成」ボタン
   - タスクの追加・編集・削除用モーダル
4. **AIタスク分解モーダル画面**
   - AIプロンプト入力欄と、生成結果（エピック、タスク、スプリント等）の確認、実行承認UI
5. **管理者画面 (refine)**
   - 全ユーザー一覧やシステム全体のプロジェクト利用状況のモニタリング画面

### 3.2 各種ビューコンポーネント仕様
- **カンバンビュー**:
  - ステータス（todo / doing / done）別のカラム構造。
  - Drag & Dropによるカラム間移動（ステータス変更）。
- **スクラムビュー**:
  - スプリントごとのタスク表示と、未割り当ての「バックログ」領域。
  - スプリントの追加、期間の変更機能。
- **ガントチャートビュー**:
  - `start_date`, `end_date` をもとにタスクをタイムライン上にバー描画。
  - 横スクロールによる期間遷移対応。

## 4. API設計
フロントエンドとバックエンド間でやり取りするRESTful APIのエンドポイント設計基本方針。

### 4.1 認証系 (Auth)
- `POST /api/auth/register` : ユーザー新規登録
- `POST /api/auth/login` : ログイン・JWTトークン発行

### 4.2 プロジェクト系 (Projects)
- `GET /api/projects` : ユーザーの所属プロジェクト一覧取得（ページネーション対応：limit, offset）
- `POST /api/projects` : 新規プロジェクト作成（オーナーとして登録）
- `GET /api/projects/{id}` : プロジェクト詳細情報取得

### 4.3 スプリント系 (Sprints)
- `GET /api/projects/{project_id}/sprints` : スプリント一覧取得（ページネーション対応：limit, offset）
- `POST /api/projects/{project_id}/sprints` : スプリント作成

### 4.4 タスク系 (Tasks)
- `GET /api/projects/{project_id}/tasks` : プロジェクト内のタスク一覧取得（ページネーション/フィルタ対応：limit, offset, status, sprint_id）
- `POST /api/projects/{project_id}/tasks` : タスク新規作成
- `PUT /api/tasks/{id}` : タスク情報編集（ステータス、期日など）
- `DELETE /api/tasks/{id}` : タスク物理削除（CASCADE削除連動）

### 4.5 AI連携系 (AI)
- `POST /api/ai/decompose` : 
  - 入力: ユーザーの自然言語要件（例「SNSアプリを作りたい」）
  - 処理: バックグラウンドタスクまたはキューに処理を登録
  - 出力: ジョブID（`job_id`）とステータスを即時返却（5秒以内）
- `GET /api/ai/decompose/{job_id}` または SSE `GET /api/ai/decompose/stream` :
  - 目的: 生成結果（エピック一覧、タスク分解リスト、推定工数、推奨スプリント）の取得・進捗確認

## 5. データベース設計 (論理モデル)
要件定義をベースにしたテーブル定義。

### 5.1 ERマッピング概要
- 1 User : N Projects
- 1 Project : N Sprints
- 1 Project : N Tasks
- 1 Sprint : N Tasks (Tasks.sprint_id は NULL 許容=バックログ)

### 5.2 テーブル定義
（※全テーブル共通で `created_at` (作成日時) と `updated_at` (更新日時) を保持する）

| テーブル名 | 役割 | Primary Key | 主なカラム |
|---|---|---|---|
| `users` | ユーザー情報 | `id` | `email`, `password_hash`, `created_at`, `updated_at` |
| `projects` | プロジェクト | `id` | `name`, `owner_id` (FK), `created_at`, `updated_at` |
| `sprints` | スプリント | `id` | `project_id` (FK), `name`, `start_date`, `end_date`, `created_at`, `updated_at` |
| `tasks` | タスクデータ | `id` | `project_id` (FK), `sprint_id` (FK), `title`, `description`, `status` (todo/doing/done), `priority`, `start_date`, `end_date`, `estimate`, `created_at`, `updated_at` |

## 6. AI統合設計 (LangGraphフロー)
要件からタスクを分解するためのパイプライン処理設計。

1. **State管理**:
   - `user_input` (string): ユーザーからの入力要件
   - `epics` (list): 抽出された大分類
   - `tasks` (list): 詳細化されたタスクリスト
2. **ノード・処理フロー** (非同期バックグラウンド実行):
   - `Parse Requirement`: 入力内容からエピック（開発の大枠）を決定。
   - `Decompose Tasks`: 各エピック毎に必要なタスクを洗い出し、推定工数とステータス初期値を付与。
   - `Plan Sprints`: 洗い出したタスクを元に、論理的なスプリント順序を構築（JSON整形）。
3. **Structured Output**: OpenAI側でのFunction Calling (Structured Outputs) を強制し、バックエンドで安全にシリアライズの上、ポーリングまたはSSE経由でフロントエンドへ提供。

## 7. セキュリティ設計
- **認証認可**: JWTを用いたステートレス認証。APIリクエスト時は Authorization ヘッダーにBearerトークンを付与。
- **データアクセス制限**: 認証ユーザーの `id` が `projects.owner_id` または関連レコードにマッチするかをAPI側で検証し、他人のプロジェクトデータ閲覧・変更を防ぐ。
- **パスワード管理**: DB保存前に bcrypt 等を用いた不可逆ハッシュ化を適用。

## 8. 非機能要件・インフラ設計
- **パフォーマンス**:
  - APIレスポンスはAI系を除き300ms以内。
  - AI自動生成レスポンスは5秒以内を目標（プロンプト最適化や並列処理の検討）。
- **デプロイメント (Docker 化環境)**:
  - `frontend`: 内部ポート3000
  - `backend`: 内部ポート8000
  - `db`: 内部ポート5432
  - これらを統括する `docker-compose.yml` を配置。
- **構成管理**: 環境依存のシークレット（JWTのSECRET_KEY、DB接続パスワード、OPENAI_API_KEY）は環境変数（`.env`）から読み込む設計とする。
