from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP

from app.core.redis import close_redis, init_redis
from app.api.routers import auth, projects, tasks, sprints, ai, admin

app = FastAPI(
    title="TaskForge API",
    description="API for the TaskForge AI-powered project management app.",
    version="1.0.0",
)

# 1. MCPの初期化
mcp = FastApiMCP(
    fastapi=app,
    name="TaskForge API MCP",
    description="MCP server for TaskForge API"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()

app.lifespan = lifespan

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
