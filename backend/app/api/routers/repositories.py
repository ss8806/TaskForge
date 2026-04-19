"""
リポジトリ管理 API ルーター
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.dependencies import CurrentUserDep, SessionDep, verify_project_access
from app.api.schemas import (
    AnalysisResultResponse,
    RepositoryCreate,
    RepositoryResponse,
)
from app.models import Repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects/{project_id}/repositories", tags=["repositories"])


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_repository(
    project_id: int,
    body: RepositoryCreate,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """リポジトリを登録"""
    # プロジェクトアクセス確認
    verify_project_access(project_id, current_user, session)

    # 既存のリポジトリを確認
    statement = select(Repository).where(Repository.project_id == project_id)
    existing = session.exec(statement).first()

    if existing:
        # 既存を更新
        existing.url = body.url
        existing.repo_type = body.repo_type
        existing.branch = body.branch
        existing.updated_at = datetime.utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    # 新規作成
    repo = Repository(
        project_id=project_id,
        url=body.url,
        repo_type=body.repo_type,
        branch=body.branch,
    )
    session.add(repo)
    session.commit()
    session.refresh(repo)

    return repo


@router.post(
    "/analyze",
    status_code=status.HTTP_202_ACCEPTED,
)
def analyze_repository(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """リポジトリを分析（同期実行）"""
    # プロジェクトアクセス確認
    verify_project_access(project_id, current_user, session)

    # リポジトリ情報を取得
    statement = select(Repository).where(Repository.project_id == project_id)
    repo = session.exec(statement).first()

    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not registered for this project",
        )

    # ローカルパスの場合は直接分析
    if repo.repo_type == "local":
        from app.services.repo_analyzer import RepositoryAnalyzer

        try:
            analyzer = RepositoryAnalyzer(repo.url)
            result = analyzer.analyze()

            # 結果を保存
            repo.analysis_result = result
            repo.last_analyzed_at = datetime.utcnow()
            repo.updated_at = datetime.utcnow()
            session.add(repo)
            session.commit()
            session.refresh(repo)

            return {
                "status": "completed",
                "result": result,
                "last_analyzed_at": repo.last_analyzed_at,
            }
        except Exception as e:
            logger.error(f"Repository analysis failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Analysis failed: {str(e)}",
            ) from e

    # GitHubリポジトリの場合は未サポート（ローカルクローンが必要）
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="GitHub repository analysis requires local clone. Please clone the repository and register as 'local' type.",
    )


@router.get("/analysis", response_model=AnalysisResultResponse)
def get_analysis_result(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """分析結果を取得"""
    # プロジェクトアクセス確認
    verify_project_access(project_id, current_user, session)

    statement = select(Repository).where(Repository.project_id == project_id)
    repo = session.exec(statement).first()

    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not registered for this project",
        )

    if not repo.analysis_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis result not available. Please run analysis first.",
        )

    result = repo.analysis_result
    return AnalysisResultResponse(
        structure=result.get("structure"),
        tech_stack=result.get("tech_stack", []),
        api_endpoints=result.get("api_endpoints", []),
        database_models=result.get("database_models", []),
        existing_features=result.get("existing_features", []),
        last_analyzed_at=repo.last_analyzed_at,
    )


@router.get("", response_model=RepositoryResponse)
def get_repository(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """登録されているリポジトリ情報を取得"""
    # プロジェクトアクセス確認
    verify_project_access(project_id, current_user, session)

    statement = select(Repository).where(Repository.project_id == project_id)
    repo = session.exec(statement).first()

    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not registered for this project",
        )

    return repo


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_repository(
    project_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """リポジトリ登録を削除"""
    # プロジェクトアクセス確認
    verify_project_access(project_id, current_user, session)

    statement = select(Repository).where(Repository.project_id == project_id)
    repo = session.exec(statement).first()

    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not registered for this project",
        )

    session.delete(repo)
    session.commit()
