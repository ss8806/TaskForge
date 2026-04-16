"""
AI連携APIルーター
Celeryによる非同期処理を使用
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies import CurrentUserDep, SessionDep, verify_project_access
from app.api.schemas import (
    AIDecompositionRequest,
    AIDecompositionResponse,
    AIDecompositionItem,
)
from app.models import Task, Sprint
from app.tasks.ai_tasks import decompose_tasks_async, get_task_status

router = APIRouter(tags=["ai"])


class AIDecompositionJobResponse(BaseModel):
    """AI分解ジョブ作成応答"""
    job_id: str = Field(description="CeleryジョブID")
    status: str = Field(description="ジョブステータス")
    message: str = Field(description="メッセージ")


class AIDecompositionStatusResponse(BaseModel):
    """AI分解ジョブステータス応答"""
    job_id: str = Field(description="CeleryジョブID")
    status: str = Field(description="ジョブステータス")
    message: str = Field(description="メッセージ")
    result: Optional[dict] = Field(None, description="結果（完了時）")
    meta: Optional[dict] = Field(None, description="メタ情報")


@router.post(
    "/projects/{project_id}/ai/decompose",
    response_model=AIDecompositionJobResponse,
    status_code=status.HTTP_202_ACCEPTED
)
def start_decomposition(
    project_id: int,
    body: AIDecompositionRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """
    AIタスク分解を非同期で開始
    ジョブIDを返し、クライアントはポーリングまたはWebhookで結果を確認
    
    処理時間: 通常10-30秒
    """
    # プロジェクトへのアクセス権限を確認
    verify_project_access(project_id, current_user, session)

    # Celeryタスクを開始
    task = decompose_tasks_async.delay(
        project_id=project_id,
        user_requirement=body.prompt,
        sprint_id=body.sprint_id
    )

    return AIDecompositionJobResponse(
        job_id=task.id,
        status="queued",
        message="AIタスク分解を開始しました。ジョブIDでステータスを確認してください。"
    )


@router.get(
    "/ai/jobs/{job_id}",
    response_model=AIDecompositionStatusResponse
)
def get_decomposition_status(
    job_id: str,
    current_user: CurrentUserDep,
):
    """
    AIタスク分解ジョブのステータスを取得
    """
    status_info = get_task_status(job_id)
    
    return AIDecompositionStatusResponse(
        job_id=job_id,
        status=status_info["status"],
        message=status_info["message"],
        result=status_info.get("result"),
        meta=status_info.get("meta")
    )


# 後方互換性のための同期エンドポイント（非推奨）
@router.post(
    "/projects/{project_id}/ai/decompose-sync",
    response_model=AIDecompositionResponse,
    deprecated=True,
    summary="同期処理（非推奨）"
)
async def decompose_tasks_sync(
    project_id: int,
    body: AIDecompositionRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """
    【非推奨】AIワークフローを同期的に実行
    処理に時間がかかるため、非同期エンドポイントの使用を推奨
    """
    import asyncio
    from app.services.ai_service import run_ai_decomposition
    
    # プロジェクトへのアクセス権限を確認
    verify_project_access(project_id, current_user, session)

    try:
        # AIワークフロー実行
        result = await run_ai_decomposition(body.prompt)

        if result["error"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI decomposition failed: {result['error']}",
            )

        # スプリントを作成（存在しない場合）
        sprint_map = {}
        for sprint_data in result["sprints"]:
            sprint = Sprint(
                project_id=project_id,
                name=sprint_data["name"],
            )
            session.add(sprint)
            session.flush()
            sprint_map[sprint_data["name"]] = sprint.id

        # タスクを作成
        for idx, task_data in enumerate(result["tasks"]):
            # スプリントIDを決定
            task_sprint_id = body.sprint_id
            if not task_sprint_id:
                for sprint_data in result["sprints"]:
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

        try:
            session.commit()
        except Exception:
            session.rollback()
            raise

        return AIDecompositionResponse(
            tasks=[
                AIDecompositionItem(
                    title=t["title"],
                    description=t.get("description"),
                    priority=t.get("priority", 2),
                    estimate=t.get("estimate"),
                )
                for t in result["tasks"]
            ]
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI decomposition failed: {str(e)}",
        )
