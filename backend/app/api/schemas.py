from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr, field_validator


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
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Sprint schemas ────────────────────────────────────────────────────────────

class SprintCreate(BaseModel):
    name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SprintResponse(BaseModel):
    id: int
    name: str
    project_id: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Task schemas ──────────────────────────────────────────────────────────────

VALID_TASK_STATUSES = {"todo", "in_progress", "review", "done"}


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: int = 2
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimate: Optional[float] = None
    sprint_id: Optional[int] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_TASK_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(sorted(VALID_TASK_STATUSES))}"
            )
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimate: Optional[float] = None
    sprint_id: Optional[int] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_TASK_STATUSES:
            raise ValueError(
                f"Invalid status '{v}'. Must be one of: {', '.join(sorted(VALID_TASK_STATUSES))}"
            )
        return v


class TaskResponse(BaseModel):
    id: int
    project_id: int
    sprint_id: Optional[int]
    title: str
    description: Optional[str]
    status: str
    priority: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    estimate: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── AI schemas ──────────────────────────────────────────────────────────────

class AIDecompositionRequest(BaseModel):
    prompt: str
    sprint_id: Optional[int] = None


class AIDecompositionItem(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 2
    estimate: Optional[float] = None


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
    task_id: Optional[int]
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
    task_id: Optional[int] = None
