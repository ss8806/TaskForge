"""
Celery タスク定義
"""

import logging

from celery.result import AsyncResult

from app.celery_app import celery_app
from app.services.ai_service import run_ai_decomposition

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="ai.decompose_tasks")
def decompose_tasks_async(
    self,
    project_id: int,
    user_requirement: str,
    sprint_id: int | None = None,
    repo_context: dict | None = None,
):
    """
    非同期でAIタスク分解を実行

    Args:
        project_id: プロジェクトID
        user_requirement: ユーザーからの要件入力
        sprint_id: タスクを追加するスプリントID（任意）
        repo_context: リポジトリ分析結果（任意）

    Returns:
        dict: 分解結果
    """
    import asyncio

    logger.info(f"Starting AI decomposition for project {project_id}")

    # タスク状態を更新
    self.update_state(
        state="PROCESSING", meta={"project_id": project_id, "progress": 0}
    )

    try:
        # 非同期関数を同期的に実行
        result = asyncio.run(run_ai_decomposition(user_requirement, repo_context=repo_context))

        if result.get("error"):
            self.update_state(state="FAILED", meta={"error": result["error"]})
            return {"status": "failed", "error": result["error"]}

        # 結果をDBに保存
        from app.db.session import get_session_context
        from app.models import Sprint, Task

        with get_session_context() as session:
            # スプリントを作成
            sprint_map = {}
            for sprint_data in result.get("sprints", []):
                sprint = Sprint(
                    project_id=project_id,
                    name=sprint_data["name"],
                )
                session.add(sprint)
                session.flush()
                sprint_map[sprint_data["name"]] = sprint.id

            # タスクを作成
            for idx, task_data in enumerate(result.get("tasks", [])):
                # スプリントIDを決定
                task_sprint_id = sprint_id
                if not task_sprint_id:
                    for sprint_data in result.get("sprints", []):
                        if idx in sprint_data.get("tasks", []):
                            task_sprint_id = sprint_map.get(sprint_data["name"])
                            break

                task = Task(
                    project_id=project_id,
                    sprint_id=task_sprint_id,
                    title=task_data.get("title", ""),
                    description=task_data.get("description", ""),
                    priority=task_data.get("priority", 2),
                    estimate=task_data.get("estimate", 8.0),
                    status="todo",
                )
                session.add(task)

            session.commit()

        logger.info(f"AI decomposition completed for project {project_id}")

        return {
            "status": "completed",
            "project_id": project_id,
            "epics": result.get("epics", []),
            "tasks_count": len(result.get("tasks", [])),
            "sprints_count": len(result.get("sprints", [])),
        }

    except Exception as e:
        logger.error(f"AI decomposition failed: {str(e)}")
        self.update_state(state="FAILED", meta={"error": str(e)})
        return {"status": "failed", "error": str(e)}


def get_task_status(task_id: str) -> dict:
    """
    タスクのステータスを取得

    Args:
        task_id: CeleryタスクID

    Returns:
        dict: タスクのステータス情報
    """
    task = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task.state,
    }

    if task.state == "PENDING":
        response["message"] = "タスクがキューに入っています"
    elif task.state == "PROCESSING":
        response["message"] = "タスクを処理中です"
        response["meta"] = task.info
    elif task.state == "SUCCESS":
        response["result"] = task.result
        response["message"] = "タスクが完了しました"
    elif task.state == "FAILURE":
        response["error"] = str(task.info)
        response["message"] = "タスクが失敗しました"
    else:
        response["message"] = f"不明なステータス: {task.state}"

    return response
