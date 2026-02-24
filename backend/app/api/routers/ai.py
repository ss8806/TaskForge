from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies import CurrentUserIdDep, SessionDep
from app.api.schemas import AIDecompositionRequest, AIDecompositionResponse, AIDecompositionItem
from app.api.routers.tasks import _verify_project_access
from app.core.config import settings
from app.models import Task, Sprint
from app.services.ai_service import run_ai_decomposition

router = APIRouter(tags=["ai"])

class AIWorkflowResponse(BaseModel):
    """AIワークフロー応答スキーマ"""
    epics: List[dict] = Field(description="抽出されたエピック一覧")
    tasks: List[dict] = Field(description="分解されたタスク一覧")
    sprints: List[dict] = Field(description="計画されたスプリント一覧")
    error: str = Field(None, description="エラーメッセージ（存在する場合）")

@router.post("/projects/{project_id}/ai/decompose", response_model=AIWorkflowResponse)
async def decompose_tasks(
    project_id: int,
    body: AIDecompositionRequest,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
):
    """
    AIワークフローを使用してタスク分解を実行
    3段階処理: エピック抽出 → タスク分解 → スプリント計画
    """
    # プロジェクトへのアクセス権限を確認
    _verify_project_access(project_id, current_user_id, session)

    try:
        # AIワークフロー実行
        result = await run_ai_decomposition(body.prompt)
        
        if result["error"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI decomposition failed: {result['error']}"
            )
        
        # スプリントを作成（存在しない場合）
        sprint_map = {}
        for sprint_data in result["sprints"]:
            sprint = Sprint(
                project_id=project_id,
                name=sprint_data["name"],
            )
            session.add(sprint)
            session.flush()  # IDを取得するためにflush
            sprint_map[sprint_data["name"]] = sprint.id
        
        # タスクを作成
        for task_data in result["tasks"]:
            # スプリントIDをマッピング（存在する場合）
            sprint_id = None
            if task_data.get("epic"):
                # エピック名からスプリントを検索（簡易実装）
                for sprint_data in result["sprints"]:
                    if task_data.get("epic") in str(sprint_data.get("tasks", [])):
                        sprint_id = sprint_map.get(sprint_data["name"])
                        break
            
            task = Task(
                project_id=project_id,
                sprint_id=sprint_id or body.sprint_id,
                title=task_data["title"],
                description=task_data.get("description", ""),
                priority=task_data.get("priority", 2),
                estimate=task_data.get("estimate", 8.0),
                status="todo",
            )
            session.add(task)
        
        session.commit()
        
        return AIWorkflowResponse(
            epics=result["epics"],
            tasks=result["tasks"],
            sprints=result["sprints"],
            error=result["error"],
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI decomposition failed: {str(e)}"
        )
