from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from sqlmodel import Session, select

from app.core.redis import close_redis, init_redis
from app.api.routers import auth, projects, tasks, sprints, ai, admin
from app.db.session import engine, get_session
from app.models import Project, Task

app = FastAPI(
    title="TaskForge API",
    description="API for the TaskForge AI-powered project management app.",
    version="1.0.0",
)

# CORS configuration - MUST BE AT THE TOP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(admin.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# ── MCP設定（重要：ルーター登録の後に書く！） ───────────────────────────────────

# 3. SSEエンドポイントをマウントします
mcp.mount_sse(mount_path="/mcp")
