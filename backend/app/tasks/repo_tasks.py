"""
リポジトリ分析 Celery タスク
"""

import logging
from datetime import datetime

from sqlmodel import select

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="repository.analyze")
def analyze_repository_async(self, project_id: int, repo_path: str) -> dict:
    """
    非同期でリポジトリ分析を実行

    Args:
        project_id: プロジェクトID
        repo_path: リポジトリのローカルパス

    Returns:
        dict: 分析結果
    """
    logger.info(f"Starting repository analysis for project {project_id}")

    # タスク状態を更新
    self.update_state(
        state="PROCESSING", meta={"project_id": project_id, "progress": 0}
    )

    try:
        from app.db.session import get_session_context
        from app.models import Repository
        from app.services.repo_analyzer import RepositoryAnalyzer

        # 分析実行
        analyzer = RepositoryAnalyzer(repo_path)
        result = analyzer.analyze()

        self.update_state(
            state="PROCESSING", meta={"project_id": project_id, "progress": 100}
        )

        # 結果をDBに保存
        with get_session_context() as session:
            statement = select(Repository).where(Repository.project_id == project_id)
            repo = session.exec(statement).first()

            if repo:
                repo.analysis_result = result
                repo.last_analyzed_at = datetime.utcnow()
                repo.updated_at = datetime.utcnow()
                session.add(repo)
                session.commit()
            else:
                logger.warning(f"Repository not found for project {project_id}")

        logger.info(f"Repository analysis completed for project {project_id}")

        return {
            "status": "completed",
            "project_id": project_id,
            "result": result,
        }

    except Exception as e:
        logger.error(f"Repository analysis failed: {str(e)}")
        self.update_state(state="FAILED", meta={"error": str(e)})
        return {"status": "failed", "error": str(e)}
