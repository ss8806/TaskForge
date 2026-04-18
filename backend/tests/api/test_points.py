"""ポイント・実績システムAPIのテスト。"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import hash_password
from app.models import Achievement, User


@pytest.fixture
def user_with_points(client: TestClient, session: Session):
    """ポイントを持つユーザーのフィクスチャ。"""
    user = User(
        email="points-user@example.com",
        password_hash=hash_password("testpassword123"),
        role="user",
        total_points=150,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def achievements(session: Session):
    """実績のフィクスチャ。"""
    achievements_data = [
        {
            "key": "first_commit",
            "title": "初回コミット",
            "description": "最初のコミット",
            "points": 100,
        },
        {
            "key": "bug_hunter",
            "title": "バグハンター",
            "description": "バグを修正",
            "points": 50,
        },
        {
            "key": "repo_cleaner",
            "title": "レポクリーナー",
            "description": "リポジトリを整理",
            "points": 30,
        },
    ]

    achievements = []
    for data in achievements_data:
        achievement = Achievement(**data)
        session.add(achievement)
        achievements.append(achievement)

    session.commit()
    return achievements


def test_get_my_points_empty(client: TestClient, user_with_points: User):
    """ユーザーのポイント取得（初期状態）。"""
    # ログイン
    login_response = client.post(
        "/api/auth/login",
        json={"email": "points-user@example.com", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # ポイント取得
    response = client.get(
        "/api/points/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_with_points.id
    assert data["total_points"] == 150
    assert data["achievements"] == []
    assert data["points_history"] == []


def test_add_points(client: TestClient, user_with_points: User):
    """ポイント追加のテスト。"""
    # ログイン
    login_response = client.post(
        "/api/auth/login",
        json={"email": "points-user@example.com", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # ポイント追加
    response = client.post(
        "/api/points/me/add",
        json={"points": 50, "reason": "タスク完了", "task_id": None},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_points"] == 200
    assert len(data["points_history"]) == 1
    assert data["points_history"][0]["points"] == 50
    assert data["points_history"][0]["reason"] == "タスク完了"


def test_add_points_negative(client: TestClient, user_with_points: User):
    """負のポイント追加のテスト。"""
    # ログイン
    login_response = client.post(
        "/api/auth/login",
        json={"email": "points-user@example.com", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # 負のポイント追加
    response = client.post(
        "/api/points/me/add",
        json={"points": -30, "reason": "タスク未完了", "task_id": None},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_points"] == 120


def test_list_achievements(client: TestClient, session: Session, achievements):
    """実績一覧の取得テスト。"""
    response = client.get("/api/points/achievements")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["key"] == "first_commit"
    assert data[0]["points"] == 100


def test_achievement_unlock(client: TestClient, user_with_points: User, achievements):
    """実績のアンロックテスト。"""
    # ログイン
    login_response = client.post(
        "/api/auth/login",
        json={"email": "points-user@example.com", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # ポイントを追加して実績アンロック
    # ユーザーは150ポイント持っており、first_commit（100ポイント）とbug_hunter（50ポイント）を取得可能
    response = client.post(
        "/api/points/me/add",
        json={"points": 10, "reason": "追加ポイント", "task_id": None},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()

    # 実績がアンロックされているか確認
    assert len(data["achievements"]) >= 2

    achievement_keys = [a["achievement"]["key"] for a in data["achievements"]]
    assert "first_commit" in achievement_keys
    assert "bug_hunter" in achievement_keys


def test_get_my_achievements(client: TestClient, user_with_points: User, achievements):
    """ユーザーの実績取得テスト。"""
    # ログイン
    login_response = client.post(
        "/api/auth/login",
        json={"email": "points-user@example.com", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # 初期状態では実績なし
    response = client.get(
        "/api/points/me/achievements", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_get_leaderboard(client: TestClient, session: Session):
    """リーダーボード取得テスト。"""
    # 複数のユーザーを作成
    users_data = [
        {"email": "user1@example.com", "points": 300},
        {"email": "user2@example.com", "points": 200},
        {"email": "user3@example.com", "points": 100},
    ]

    for data in users_data:
        user = User(
            email=data["email"],
            password_hash=hash_password("testpassword123"),
            role="user",
            total_points=data["points"],
        )
        session.add(user)

    session.commit()

    # リーダーボード取得
    response = client.get("/api/points/leaderboard?limit=10")
    assert response.status_code == 200
    data = response.json()

    # ポイントの降順でソートされている
    assert len(data) >= 3
    assert data[0]["total_points"] >= data[1]["total_points"]  # type: ignore[index]
    assert data[1]["total_points"] >= data[2]["total_points"]  # type: ignore[index]


def test_points_history_ordering(client: TestClient, user_with_points: User):
    """ポイント履歴の順序テスト（最新順）。"""
    # ログイン
    login_response = client.post(
        "/api/auth/login",
        json={"email": "points-user@example.com", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # 複数のポイントを追加
    client.post(
        "/api/points/me/add",
        json={"points": 10, "reason": "追加1", "task_id": None},
        headers={"Authorization": f"Bearer {token}"},
    )

    client.post(
        "/api/points/me/add",
        json={"points": 20, "reason": "追加2", "task_id": None},
        headers={"Authorization": f"Bearer {token}"},
    )

    # ポイント取得
    response = client.get(
        "/api/points/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()

    # 履歴が最新順であることを確認
    assert len(data["points_history"]) == 2
    assert data["points_history"][0]["reason"] == "追加2"
    assert data["points_history"][1]["reason"] == "追加1"


def test_unauthenticated_points_access(client: TestClient):
    """認証なしでのポイントAPIアクセス拒否テスト。"""
    response = client.get("/api/points/me")
    assert response.status_code in (401, 403)

    response = client.post("/api/points/me/add", json={"points": 10, "reason": "test"})
    assert response.status_code in (401, 403)
