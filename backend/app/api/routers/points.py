from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

from app.api.dependencies import CurrentUserDep, SessionDep
from app.api.schemas import (
    AddPointsRequest,
    AchievementResponse,
    PointsHistoryResponse,
    UserAchievementResponse,
    UserPointsResponse,
)
from app.models import Achievement, PointsHistory, User, UserAchievement

router = APIRouter(prefix="/points", tags=["points"])


# ── User Points ─────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserPointsResponse)
def get_my_points(
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """Get current user's points, achievements, and history."""
    achievements = session.exec(
        select(UserAchievement)
        .where(UserAchievement.user_id == current_user.id)
        .order_by(UserAchievement.unlocked_at.desc())
    ).all()

    history = session.exec(
        select(PointsHistory)
        .where(PointsHistory.user_id == current_user.id)
        .order_by(PointsHistory.created_at.desc())
        .limit(50)
    ).all()

    return UserPointsResponse(
        user_id=current_user.id,
        total_points=current_user.total_points,
        achievements=achievements,
        points_history=history,
    )


@router.post("/me/add", response_model=UserPointsResponse)
def add_points(
    body: AddPointsRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """Add points to current user."""
    # Create points history record
    history = PointsHistory(
        user_id=current_user.id,
        points=body.points,
        reason=body.reason,
        task_id=body.task_id,
    )
    session.add(history)

    # Update user total points
    current_user.total_points += body.points

    # Check for achievements to unlock
    check_and_unlock_achievements(session, current_user)

    session.commit()
    session.refresh(current_user)

    return get_my_points(session, current_user)


# ── Achievements ────────────────────────────────────────────────────────────

@router.get("/achievements", response_model=List[AchievementResponse])
def list_achievements(
    session: SessionDep,
):
    """List all available achievements."""
    achievements = session.exec(select(Achievement)).all()
    return achievements


@router.get("/me/achievements", response_model=List[UserAchievementResponse])
def get_my_achievements(
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """Get current user's unlocked achievements."""
    achievements = session.exec(
        select(UserAchievement)
        .where(UserAchievement.user_id == current_user.id)
        .order_by(UserAchievement.unlocked_at.desc())
    ).all()
    return achievements


# ── Leaderboard ─────────────────────────────────────────────────────────────

@router.get("/leaderboard")
def get_leaderboard(
    session: SessionDep,
    limit: int = 10,
):
    """Get top users by points."""
    users = session.exec(
        select(User)
        .order_by(User.total_points.desc())
        .limit(limit)
    ).all()

    return [
        {
            "user_id": user.id,
            "email": user.email,
            "total_points": user.total_points,
        }
        for user in users
    ]


# ── Helper Functions ─────────────────────────────────────────────────────────

def check_and_unlock_achievements(session: Session, user: User):
    """Check and unlock achievements based on user's point total."""
    achievements = session.exec(select(Achievement)).all()

    for achievement in achievements:
        # Check if user already has this achievement
        existing = session.exec(
            select(UserAchievement)
            .where(
                UserAchievement.user_id == user.id,
                UserAchievement.achievement_id == achievement.id,
            )
        ).first()

        if existing:
            continue

        # Unlock achievement if user has enough points
        if user.total_points >= achievement.points:
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
            )
            session.add(user_achievement)


def add_points_to_user(
    session: Session,
    user_id: int,
    points: int,
    reason: str,
    task_id: int | None = None,
):
    """Helper function to add points to a user."""
    user = session.get(User, user_id)
    if user:
        user.total_points += points

        history = PointsHistory(
            user_id=user_id,
            points=points,
            reason=reason,
            task_id=task_id,
        )
        session.add(history)

        # Check for achievements
        check_and_unlock_achievements(session, user)
