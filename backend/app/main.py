from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.redis import close_redis, init_redis
from app.api.routers import auth, projects, tasks, sprints


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()


app = FastAPI(
    title="TaskForge API",
    description="API for the TaskForge AI-powered project management app.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # NOTE: Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ルーター登録 ──────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(sprints.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
