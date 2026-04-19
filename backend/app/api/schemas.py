from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, EmailStr, field_validator

# ── Paginated Response ────────────────────────────────────────────────────────

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """ページネーション付きレスポンススキーマ"""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ── Auth schemas ──────────────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Project schemas ───────────────────────────────────────────────────────────


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Sprint schemas ────────────────────────────────────────────────────────────


class SprintCreate(BaseModel):
    name: str
    start_date: datetime | None = None
    end_date: datetime | None = None


class SprintResponse(BaseModel):
    id: int
    name: str
    project_id: int
    start_date: datetime | None
    end_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Task schemas ──────────────────────────────────────────────────────────────

VALID_TASK_STATUSES = {"todo", "doing", "done"}


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: str = "todo"
    priority: int = 2
    start_date: datetime | None = None
    end_date: datetime | None = None
    estimate: float | None = None
    sprint_id: int | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_TASK_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(sorted(VALID_TASK_STATUSES))}"
            )
        return v


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    estimate: float | None = None
    sprint_id: int | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_TASK_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(sorted(VALID_TASK_STATUSES))}"
            )
        return v


class TaskResponse(BaseModel):
    id: int
    project_id: int
    sprint_id: int | None
    title: str
    description: str | None
    status: str
    priority: int
    start_date: datetime | None
    end_date: datetime | None
    estimate: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── AI schemas ──────────────────────────────────────────────────────────────


class AIDecompositionRequest(BaseModel):
    prompt: str
    sprint_id: int | None = None


class AIDecompositionItem(BaseModel):
    title: str
    description: str | None = None
    priority: int = 2
    estimate: float | None = None


class AIDecompositionResponse(BaseModel):
    tasks: list[AIDecompositionItem]


# ── Points & Achievements schemas ────────────────────────────────────────────


class AchievementResponse(BaseModel):
    id: int
    key: str
    title: str
    description: str
    points: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UserAchievementResponse(BaseModel):
    id: int
    achievement_id: int
    unlocked_at: datetime
    achievement: AchievementResponse

    model_config = {"from_attributes": True}


class PointsHistoryResponse(BaseModel):
    id: int
    points: int
    reason: str
    task_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPointsResponse(BaseModel):
    user_id: int
    total_points: int
    achievements: list[UserAchievementResponse]
    points_history: list[PointsHistoryResponse]

    model_config = {"from_attributes": True}


class AddPointsRequest(BaseModel):
    points: int
    reason: str
    task_id: int | None = None


# ── Repository schemas ───────────────────────────────────────────────────────


class RepositoryCreate(BaseModel):
    url: str
    repo_type: str = "github"
    branch: str = "main"


class RepositoryResponse(BaseModel):
    id: int
    project_id: int
    url: str
    repo_type: str
    branch: str
    analysis_result: dict | None
    last_analyzed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnalysisResultResponse(BaseModel):
    """分析結果レスポンス"""

    structure: dict | None = None
    tech_stack: list[str] = []
    api_endpoints: list[dict] = []
    database_models: list[dict] = []
    existing_features: list[str] = []
    last_analyzed_at: datetime | None = None
