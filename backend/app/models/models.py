"""SQLModel database models."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """ユーザーモデル"""

    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    role: str = Field(default="user", nullable=False)
    total_points: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    projects: list["Project"] = Relationship(back_populates="owner")
    user_achievements: list["UserAchievement"] = Relationship(back_populates="user")
    points_history: list["PointsHistory"] = Relationship(back_populates="user")


class Project(SQLModel, table=True):
    """プロジェクトモデル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    owner_id: int = Field(foreign_key="user.id", ondelete="CASCADE", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    owner: User = Relationship(back_populates="projects")
    sprints: list["Sprint"] = Relationship(back_populates="project")
    tasks: list["Task"] = Relationship(back_populates="project")


class Sprint(SQLModel, table=True):
    """スプリントモデル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", ondelete="CASCADE", nullable=False)
    name: str = Field(nullable=False)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    project: Project = Relationship(back_populates="sprints")
    tasks: list["Task"] = Relationship(back_populates="sprint")


class Task(SQLModel, table=True):
    """タスクモデル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", ondelete="CASCADE", nullable=False)
    sprint_id: Optional[int] = Field(default=None, foreign_key="sprint.id")
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    status: str = Field(default="todo", nullable=False)
    priority: int = Field(default=0, nullable=False)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    estimate: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    project: Project = Relationship(back_populates="tasks")
    sprint: Optional[Sprint] = Relationship(back_populates="tasks")


class Achievement(SQLModel, table=True):
    """実績モデル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True, nullable=False)
    name: str = Field(nullable=False)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    points: int = Field(default=0, nullable=False)
    icon: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user_achievements: list["UserAchievement"] = Relationship(back_populates="achievement")


class UserAchievement(SQLModel, table=True):
    """ユーザー実績モデル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE", nullable=False)
    achievement_id: int = Field(foreign_key="achievement.id", ondelete="CASCADE", nullable=False)
    unlocked_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: User = Relationship(back_populates="user_achievements")
    achievement: Achievement = Relationship(back_populates="user_achievements")


class PointsHistory(SQLModel, table=True):
    """ポイント履歴モデル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE", nullable=False)
    points: int = Field(nullable=False)
    reason: Optional[str] = Field(default=None)
    task_id: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: User = Relationship(back_populates="points_history")
