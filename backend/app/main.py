from contextlib import asynccontextmanager
import logging
import sys
from fastapi import Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlmodel import Session, select

from app.core.config import settings
from app.core.redis import close_redis, init_redis
from app.api.routers import auth, points, projects, tasks, sprints, ai, admin
from app.api.error_handlers import register_error_handlers
from app.api.dependencies import get_current_user
from app.db.session import engine, get_session
from app.models import Project, Task, User

# 構造化ログの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# レート制限の設定（fastapi-mcpとの互換性を考慮して手動実装）
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10/minute"],
    storage_uri="memory://"
)

# レート制限超過時のエラーハンドラー
def rate_limit_handler(request: any, exc: RateLimitExceeded):
    """レート制限超過時のハンドラー"""
    return {
        "detail": f"レート制限を超過しました: {exc.detail}",
        "status": status.HTTP_429_TOO_MANY_REQUESTS
    }

app = FastAPI(
    title="TaskForge API",
    description="API for the TaskForge AI-powered project management app.",
    version="1.0.0",
)

# エラーハンドラーの登録
register_error_handlers(app)

# CORS configuration - MUST BE AT THE TOP
# セキュリティ強化: 許可されたオリジンのみを許可
allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. MCPの初期化
mcp = FastApiMCP(
    fastapi=app,
    name="TaskForge API MCP",
    description="MCP server for TaskForge API"
)

# --- MCP Compatible Routes (Automatically exposed as tools) ---

@app.get("/mcp/projects", tags=["mcp"])
def list_projects_mcp(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List all projects available in TaskForge. Requires authentication."""
    statement = select(Project).where(Project.owner_id == current_user.id)
    projects_list = session.exec(statement).all()
    return projects_list

@app.get("/mcp/tasks/{project_id}", tags=["mcp"])
def list_tasks_mcp(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List all tasks for a specific project by project_id. Requires authentication."""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    statement = select(Task).where(Task.project_id == project_id)
    tasks_list = session.exec(statement).all()
    return tasks_list

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()

app.lifespan = lifespan

# ── ルーター登録 ──────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(sprints.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(points.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/health")
async def health_check(session: Session = Depends(get_session)):
    """ヘルスチェック - DBとRedisの接続状態を確認"""
    health_status = {"status": "ok"}
    
    # DBチェック
    try:
        session.exec(select(1)).first()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = "error"
        health_status["status"] = "degraded"
    
    # Redisチェック
    try:
        from app.core.redis import redis_client
        if redis_client:
            await redis_client.ping()
            health_status["redis"] = "connected"
        else:
            health_status["redis"] = "not_initialized"
    except Exception as e:
        health_status["redis"] = "error"
        health_status["status"] = "degraded"
    
    return health_status

# ── MCP設定（重要：ルーター登録の後に書く！） ───────────────────────────────────

# 3. SSEエンドポイントをマウントします
mcp.mount_sse(mount_path="/mcp")
