from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import select

from app.api.dependencies import SessionDep, AdminDep
from app.api.schemas import UserResponse, ProjectResponse
from app.models import User, Project

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
def list_users(
    session: SessionDep,
    admin_user: AdminDep,
):
    """
    管理者用：全ユーザー一覧を取得
    """
    users = session.exec(select(User)).all()
    return users


@router.get("/projects", response_model=List[ProjectResponse])
def list_all_projects(
    session: SessionDep,
    admin_user: AdminDep,
):
    """
    管理者用：全プロジェクト一覧を取得
    """
    projects = session.exec(select(Project)).all()
    return projects


@router.post("/users/{user_id}/make-admin")
def make_user_admin(
    user_id: int,
    session: SessionDep,
    admin_user: AdminDep,
):
    """
    管理者用：ユーザーを管理者に昇格
    """
    user = session.get(User, user_id)
    if not user:
        return {"detail": "User not found"}
    
    user.role = "admin"
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"detail": f"User {user.email} promoted to admin"}


@router.post("/users/{user_id}/revoke-admin")
def revoke_user_admin(
    user_id: int,
    session: SessionDep,
    admin_user: AdminDep,
):
    """
    管理者用：ユーザーの管理者権限を剥奪
    """
    # 自分自身の管理者権限を剥奪できないようにチェック
    if user_id == admin_user.id:
        return {"detail": "Cannot revoke your own admin privileges"}
    
    user = session.get(User, user_id)
    if not user:
        return {"detail": "User not found"}
    
    user.role = "user"
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"detail": f"User {user.email} admin privileges revoked"}