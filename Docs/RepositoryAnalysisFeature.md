# リポジトリ分析機能 設計ドキュメント

## 1. 概要

### 1.1 目的
リポジトリ分析機能は、既存のコードベースを解析し、その情報をAIタスク分解に統合することで、より現実的で実装可能なタスク分解を実現する。

### 1.2 背景
従来のAIタスク分解は、ユーザーの要件テキストのみでタスクを生成していたため、以下の課題があった：
- 既存機能との重複提案
- 既存アーキテクチャに合わないタスク生成
- 技術スタックの不一致
- 依存関係の考慮不足

### 1.3 解決策
プロジェクトのリポジトリ（コードベース）を分析し、以下の情報をAI分解にコンテキストとして提供する：
- ディレクトリ構造
- 使用技術スタック
- 既存機能一覧
- APIエンドポイント
- データベースモデル

---

## 2. アーキテクチャ設計

### 2.1 コンポーネント構成

```
┌─────────────────────────────────────────────────────┐
│                   フロントエンド                     │
│  ┌─────────────────┐    ┌──────────────────────┐    │
│  │ リポジトリ登録UI │    │ AI分解実行UI         │    │
│  └────────┬────────┘    └──────────┬───────────┘    │
└───────────┼────────────────────────┼────────────────┘
            │                        │
            ▼                        ▼
┌─────────────────────────────────────────────────────┐
│                 バックエンド API                     │
│  ┌─────────────────┐    ┌──────────────────────┐    │
│  │ /repositories   │    │ /ai/decompose        │    │
│  │ (リポジトリ管理) │    │ (AI分解)             │    │
│  └────────┬────────┘    └──────────┬───────────┘    │
└───────────┼────────────────────────┼────────────────┘
            │                        │
            ▼                        ▼
┌──────────────────────┐  ┌──────────────────────────┐
│ RepositoryAnalyzer   │  │ AIService                │
│ (リポジトリ分析)     │  │ (AIタスク分解)           │
│                      │  │                          │
│ ・ディレクトリ解析   │  │ ・リポジトリ情報を       │
│ ・技術スタック検出   │◄─┤   コンテキストとして使用 │
│ ・コード解析         │  │ ・プロンプトに埋め込み   │
└──────────┬───────────┘  └──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│                  データベース                        │
│  ┌──────────────────────────────────────────────┐   │
│  │ Repository モデル                             │   │
│  │ - プロジェクトとのリレーション                │   │
│  │ - 分析結果のキャッシュ                        │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 2.2 データフロー

```
1. ユーザーがGitHubリポジトリURLまたはローカルパスを登録
2. RepositoryAnalyzerがリポジトリを分析
3. 分析結果をデータベースに保存
4. AI分解実行時に、分析結果をコンテキストとして取得
5. AIServiceがリポジトリ情報を含むプロンプトでタスク分解
6. 結果を返却
```

---

## 3. バックエンド詳細設計

### 3.1 データモデル

#### 3.1.1 Repository モデル（新規追加）

```python
class Repository(SQLModel, table=True):
    """リポジトリ情報"""
    
    __tablename__ = "repositories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", unique=True)
    url: str = Field(description="GitHubリポジトリURLまたはローカルパス")
    repo_type: str = Field(default="github", description="github | local")
    branch: str = Field(default="main", description="対象ブランチ")
    
    # 分析結果（キャッシュ）
    analysis_result: Optional[dict] = Field(
        sa_column=Column(JSON),
        default=None,
        description="分析結果のJSON"
    )
    last_analyzed_at: Optional[datetime] = Field(default=None)
    
    # タイムスタンプ
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # リレーション
    project: Project = Relationship(back_populates="repository")
```

#### 3.1.2 Project モデル（拡張）

```python
class Project(SQLModel, table=True):
    # ... existing fields ...
    
    # 新規追加
    repository: Optional["Repository"] = Relationship(back_populates="project")
```

### 3.2 リポジトリ分析サービス

#### 3.2.1 RepositoryAnalyzer クラス

```python
# backend/app/services/repo_analyzer.py

class RepositoryAnalyzer:
    """リポジトリ分析サービス"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        
    def analyze(self) -> dict:
        """リポジトリを包括的に分析"""
        return {
            "structure": self._analyze_structure(),
            "tech_stack": self._detect_tech_stack(),
            "api_endpoints": self._extract_api_endpoints(),
            "database_models": self._extract_db_models(),
            "existing_features": self._identify_features(),
        }
    
    def _analyze_structure(self) -> dict:
        """ディレクトリ構造を解析"""
        # os.walk または pathlib で再帰的に解析
        # .gitignore を考慮
        pass
    
    def _detect_tech_stack(self) -> list[str]:
        """使用技術スタックを検出"""
        tech_stack = []
        
        # フレームワーク検出
        if (self.repo_path / "package.json").exists():
            tech_stack.append("Node.js")
            # dependencies からフレームワーク特定
            
        if (self.repo_path / "pyproject.toml").exists():
            tech_stack.append("Python")
            
        if (self.repo_path / "requirements.txt").exists():
            tech_stack.append("Python")
            
        return tech_stack
    
    def _extract_api_endpoints(self) -> list[dict]:
        """APIエンドポイントを抽出"""
        # FastAPIのrouter定義を解析
        # @router.get, @router.post などを検出
        pass
    
    def _extract_db_models(self) -> list[dict]:
        """データベースモデルを抽出"""
        # SQLModel定義を解析
        # class ...(SQLModel, table=True) を検出
        pass
    
    def _identify_features(self) -> list[str]:
        """既存機能を特定"""
        # ディレクトリ名、ファイル名から機能を推測
        # routers/, services/, components/ などを解析
        pass
```

### 3.3 AIサービス改善

#### 3.3.1 run_ai_decomposition 関数（拡張）

```python
# backend/app/services/ai_service.py

async def run_ai_decomposition(
    user_requirement: str,
    repo_context: dict | None = None  # 新規追加
) -> dict:
    """
    AIワークフローを実行
    
    Args:
        user_requirement: ユーザーからの要件入力
        repo_context: リポジトリ分析結果（オプション）
            {
                "structure": {...},
                "tech_stack": ["Python", "FastAPI", ...],
                "api_endpoints": [...],
                "database_models": [...],
                "existing_features": [...]
            }
    
    Returns:
        dict: タスク分解結果
    """
    workflow = create_ai_workflow()
    
    initial_state: WorkflowState = {
        "user_requirement": user_requirement,
        "repo_context": repo_context,  # 追加
        "epics": [],
        "tasks": [],
        "sprints": [],
        "error": None,
    }
    
    result = workflow.invoke(initial_state)
    
    return {
        "epics": result["epics"],
        "tasks": result["tasks"],
        "sprints": result["sprints"],
        "error": result["error"],
    }
```

#### 3.3.2 プロンプト改善例

```python
def extract_epics_node(state: WorkflowState) -> WorkflowState:
    """要件からエピックを抽出（リポジトリ情報付き）"""
    llm = get_llm()
    
    repo_context = state.get("repo_context")
    
    # リポジトリ情報がある場合はプロンプトに追加
    context_section = ""
    if repo_context:
        context_section = f"""
## 既存プロジェクト情報
- 技術スタック: {', '.join(repo_context.get('tech_stack', []))}
- 既存機能: {', '.join(repo_context.get('existing_features', []))}
- 既存API: {len(repo_context.get('api_endpoints', []))}個

## 注意事項
- 既存機能と重複するタスクは作成しないでください
- 既存の技術スタックに従ってください
- 既存のAPIを活用してください
"""
    
    prompt = f"""
{context_section}

## 新しい要件
{state["user_requirement"]}

## タスク
上記の要件を満たすためのエピックを抽出してください。
"""
    
    # ... 以降既存の処理 ...
```

### 3.4 API エンドポイント

#### 3.4.1 リポジトリ管理API

```python
# backend/app/api/routers/repositories.py

@router.post(
    "/projects/{project_id}/repositories",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_repository(
    project_id: int,
    body: RepositoryCreate,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """リポジトリを登録"""
    pass

@router.post("/projects/{project_id}/repositories/analyze")
def analyze_repository(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """リポジトリを分析（非同期）"""
    pass

@router.get("/projects/{project_id}/repositories/analysis")
def get_analysis_result(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """分析結果を取得"""
    pass
```

#### 3.4.2 AI分解API（拡張）

```python
# backend/app/api/routers/ai.py

@router.post("/projects/{project_id}/ai/decompose")
def start_decomposition(
    project_id: int,
    body: AIDecompositionRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """AIタスク分解を開始（リポジトリ情報を自動取得）"""
    
    # リポジトリ分析結果を取得
    repo_context = get_repository_context(project_id, session)
    
    # Celeryタスクにリポジトリ情報を渡す
    task = decompose_tasks_async.delay(
        project_id=project_id,
        user_requirement=body.prompt,
        sprint_id=body.sprint_id,
        repo_context=repo_context,  # 追加
    )
    
    return AIDecompositionJobResponse(...)
```

---

## 4. Celeryタスク設計

### 4.1 非同期分析タスク

```python
# backend/app/tasks/repo_tasks.py

@celery_app.task(bind=True, name="repository.analyze")
def analyze_repository_async(self, project_id: int, repo_path: str):
    """リポジトリ分析を非同期で実行"""
    
    self.update_state(state="PROCESSING", meta={"progress": 0})
    
    try:
        # 分析実行
        analyzer = RepositoryAnalyzer(repo_path)
        result = analyzer.analyze()
        
        # 結果をDBに保存
        with get_session_context() as session:
            repo = session.exec(
                select(Repository).where(Repository.project_id == project_id)
            ).first()
            
            if repo:
                repo.analysis_result = result
                repo.last_analyzed_at = datetime.utcnow()
                session.commit()
        
        return {"status": "completed", "result": result}
        
    except Exception as e:
        self.update_state(state="FAILED", meta={"error": str(e)})
        return {"status": "failed", "error": str(e)}
```

### 4.2 AI分解タスク（拡張）

```python
# backend/app/tasks/ai_tasks.py

@celery_app.task(bind=True, name="ai.decompose_tasks")
def decompose_tasks_async(
    self,
    project_id: int,
    user_requirement: str,
    sprint_id: int | None = None,
    repo_context: dict | None = None,  # 新規追加
):
    """AIタスク分解（リポジトリ情報付き）"""
    
    try:
        # リポジトリ情報を渡してAI分解実行
        result = asyncio.run(
            run_ai_decomposition(
                user_requirement,
                repo_context=repo_context
            )
        )
        
        # ... 以降既存の処理 ...
        
    except Exception as e:
        logger.error(f"AI decomposition failed: {str(e)}")
        self.update_state(state="FAILED", meta={"error": str(e)})
        return {"status": "failed", "error": str(e)}
```

---

## 5. フロントエンド設計

### 5.1 コンポーネント構成

```
frontend/src/
├── components/
│   └── features/
│       ├── RepositorySettings.tsx       # リポジトリ設定UI
│       ├── RepositoryAnalysisResult.tsx # 分析結果表示
│       └── AIDecompositionModal.tsx     # AI分解UI（既存改善）
├── hooks/
│   └── useRepository.ts                 # リポジトリ操作用フック
└── types/
    └── generated.ts                     # OpenAPIから自動生成
```

### 5.2 リポジトリ設定コンポーネント

```typescript
// frontend/src/components/features/RepositorySettings.tsx

interface RepositorySettingsProps {
  projectId: number;
}

export function RepositorySettings({ projectId }: RepositorySettingsProps) {
  const [repoUrl, setRepoUrl] = useState('');
  const [repoType, setRepoType] = useState<'github' | 'local'>('github');
  
  const mutation = useMutation({
    mutationFn: (data: RepositoryCreate) => 
      repositoriesApi.create(projectId, data),
    onSuccess: () => {
      // 分析を開始
      analyzeMutation.mutate({ projectId });
    },
  });
  
  const analyzeMutation = useMutation({
    mutationFn: () => repositoriesApi.analyze(projectId),
    onSuccess: () => {
      // ポーリングで分析結果を確認
    },
  });
  
  return (
    <div>
      <h2>リポジトリ設定</h2>
      <form onSubmit={handleSubmit(mutation.mutate)}>
        <select value={repoType} onChange={e => setRepoType(e.target.value)}>
          <option value="github">GitHub</option>
          <option value="local">ローカル</option>
        </select>
        
        <input
          type="text"
          value={repoUrl}
          onChange={e => setRepoUrl(e.target.value)}
          placeholder={repoType === 'github' 
            ? 'https://github.com/user/repo' 
            : '/path/to/repo'}
        />
        
        <button type="submit">登録して分析</button>
      </form>
    </div>
  );
}
```

### 5.3 AI分解実行フロー

```typescript
// 改善されたAI分解実行
async function handleAIDecomposition(prompt: string) {
  // 1. リポジトリ分析結果の有無を確認
  const analysis = await repositoriesApi.getAnalysis(projectId);
  
  // 2. AI分解を実行（バックエンドが自動的にリポジトリ情報を使用）
  const job = await aiApi.decompose(projectId, {
    prompt,
    sprint_id: selectedSprintId,
  });
  
  // 3. ポーリングで結果を取得
  const result = await pollJobStatus(job.job_id);
  
  return result;
}
```

---

## 6. 実装計画

### Phase 1: 基本機能（1-2日）

#### 6.1.1 データモデル追加
- [ ] Repository モデル定義
- [ ] Alembic マイグレーション作成
- [ ] Project モデルにリレーション追加

#### 6.1.2 リポジトリ分析サービス（基本）
- [ ] ディレクトリ構造解析
- [ ] 技術スタック検出
- [ ] ファイル一覧取得

#### 6.1.3 API エンドポイント
- [ ] POST /projects/{id}/repositories
- [ ] POST /projects/{id}/repositories/analyze
- [ ] GET /projects/{id}/repositories/analysis

### Phase 2: コード解析（2-3日）

#### 6.2.1 高度な解析
- [ ] Python import文解析
- [ ] TypeScript import/export解析
- [ ] FastAPIルーター自動検出
- [ ] データベースモデル抽出

#### 6.2.2 分析結果キャッシュ
- [ ] 分析結果をDBに保存
- [ ] 最終分析日時管理
- [ ] 再分析トリガー

### Phase 3: AI統合（1-2日）

#### 6.3.1 AIサービス改善
- [ ] run_ai_decomposition に repo_context 引数追加
- [ ] プロンプト改善
- [ ] ワークフロー状態定義更新

#### 6.3.2 Celeryタスク更新
- [ ] analyze_repository_async タスク作成
- [ ] decompose_tasks_async タスク拡張

#### 6.3.3 フロントエンド
- [ ] リポジトリ設定UI
- [ ] 分析結果表示
- [ ] AI分解UI改善

---

## 7. テスト計画

### 7.1 ユニットテスト

```python
# tests/services/test_repo_analyzer.py

def test_analyze_directory_structure():
    analyzer = RepositoryAnalyzer("/path/to/repo")
    result = analyzer._analyze_structure()
    assert "backend" in result
    assert "frontend" in result

def test_detect_tech_stack():
    analyzer = RepositoryAnalyzer("/path/to/repo")
    result = analyzer._detect_tech_stack()
    assert "Python" in result
    assert "FastAPI" in result
```

### 7.2 統合テスト

```python
# tests/api/test_repositories.py

def test_register_repository(client, auth_headers):
    response = client.post(
        "/projects/1/repositories",
        json={"url": "https://github.com/user/repo", "repo_type": "github"},
        headers=auth_headers,
    )
    assert response.status_code == 201

def test_analyze_repository(client, auth_headers):
    response = client.post(
        "/projects/1/repositories/analyze",
        headers=auth_headers,
    )
    assert response.status_code == 202
```

---

## 8. 制限事項と今後の改善

### 8.1 制限事項（Phase 1）

1. **対応言語**: Python, TypeScript/JavaScript のみ
2. **GitHub連携**: URL登録のみ（クローンは手動）
3. **解析深度**: ファイルレベル（AST解析なし）
4. **プライベートリポジトリ**: 未対応（要アクセストークン）

### 8.2 今後の改善（Phase 4以降）

1. **AST解析**: tree-sitter による詳細なコード解析
2. **依存関係グラフ**: 関数・クラスレベルの依存関係可視化
3. **GitHub API連携**: Webhook による自動再分析
4. **複数ブランチ対応**: featureブランチごとの分析
5. **コード品質メトリクス**: 複雑度、テストカバレッジ等
6. **他言語対応**: Go, Rust, Java など

---

## 9. 環境設定

### 9.1 環境変数

```bash
# .env

# リポジトリ分析設定
REPO_ANALYSIS_ENABLED=true
REPO_CLONE_DIR=/tmp/taskforge/repos

# GitHub API（プライベートリポジトリ用）
GITHUB_ACCESS_TOKEN=ghp_xxxx
```

### 9.2 依存パッケージ

```toml
# pyproject.toml

[project]
dependencies = [
    # 既存...
    
    # リポジトリ分析用（Phase 2以降）
    # "tree-sitter>=0.20.0",
    # "tree-sitter-python>=0.20.0",
    # "tree-sitter-typescript>=0.20.0",
    # "networkx>=3.0",
]
```

---

## 10. エラーハンドリング

### 10.1 想定されるエラー

| エラー | 原因 | 対応 |
|--------|------|------|
| RepositoryNotFoundError | リポジトリが存在しない | 404エラー返却 |
| InvalidRepositoryError | Gitリポジトリではない | 400エラー返却 |
| AnalysisTimeoutError | 分析がタイムアウト | 再試行を促す |
| PermissionError | アクセス権限なし | 403エラー返却 |

### 10.2 エラーレスポンス例

```json
{
  "error": "InvalidRepositoryError",
  "detail": "指定されたパスは有効なGitリポジトリではありません",
  "suggestion": "git init を実行してから再度お試しください"
}
```

---

## 11. セキュリティ考慮事項

### 11.1 ローカルリポジトリ アクセス

- パス解決時にディレクトリトラバーサル対策
- 許可されたディレクトリ配下のみアクセス可能
- シンボリックリンクの解決制限

### 11.2 GitHub アクセストークン

- 環境変数で管理（.env）
- DBには保存しない
- ログに出力しない

### 11.3 分析結果のアクセス制御

- プロジェクト所有者のみ閲覧可能
- APIエンドポイントに認証必須

---

## 12. パフォーマンス最適化

### 12.1 キャッシュ戦略

- 分析結果をDBにキャッシュ
- 最終分析から24時間はキャッシュを使用
- 明示的な再分析で更新

### 12.2 非同期処理

- リポジトリ分析はCeleryで非同期実行
- 大規模リポジトリはタイムアウト設定（5分）
- 進捗状況をWebSocketまたはポーリングで通知

### 12.3 解析対象のフィルタリング

- node_modules, .venv, __pycache__ 等を除外
- .gitignore を尊重
- 最大ファイル数制限（10,000ファイル）

---

## 13. 用語集

| 用語 | 説明 |
|------|------|
| リポジトリ分析 | コードベースの構造、技術スタック、既存機能などを自動的に解析する処理 |
| repo_context | 分析結果の構造化データ。AI分解のコンテキストとして使用 |
| AST | Abstract Syntax Tree（抽象構文木）。コードの構造的表現 |
| エピック | 大きな機能のまとまり。タスク分解の上位概念 |

---

## 14. 参考文献

- [TaskForge 基本設計書](./BasicDesign.md)
- [TaskForge 詳細設計書](./DetailedDesign.md)
- [TaskForge API仕様書](./APISpecification.md)
- [LangGraph ドキュメント](https://langchain-ai.github.io/langgraph/)
- [FastAPI ドキュメント](https://fastapi.tiangolo.com/)
