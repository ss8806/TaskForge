from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


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

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: int = 2
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimate: Optional[float] = None
    sprint_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimate: Optional[float] = None
    sprint_id: Optional[int] = None


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
