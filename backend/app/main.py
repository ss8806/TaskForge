from contextlib import asynccontextmanager
from fastapi import Depends, status
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
from app.db.session import engine, get_session
from app.models import Project, Task

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
def list_projects_mcp(session: Session = Depends(get_session)):
    """List all projects available in TaskForge."""
    statement = select(Project)
    projects = session.exec(statement).all()
    return projects

@app.get("/mcp/tasks/{project_id}", tags=["mcp"])
def list_tasks_mcp(project_id: int, session: Session = Depends(get_session)):
    """List all tasks for a specific project by project_id."""
    statement = select(Task).where(Task.project_id == project_id)
    tasks = session.exec(statement).all()
    return tasks

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
def health_check():
    return {"status": "ok"}

# ── MCP設定（重要：ルーター登録の後に書く！） ───────────────────────────────────

# 3. SSEエンドポイントをマウントします
mcp.mount_sse(mount_path="/mcp")
