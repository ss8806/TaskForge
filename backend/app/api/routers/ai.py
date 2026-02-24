from typing import List
from fastapi import APIRouter, HTTPException, status
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.api.dependencies import CurrentUserIdDep, SessionDep
from app.api.schemas import AIDecompositionRequest, AIDecompositionResponse, AIDecompositionItem
from app.api.routers.tasks import _verify_project_access
from app.core.config import settings
from app.models import Task

router = APIRouter(tags=["ai"])

class TaskList(BaseModel):
    tasks: List[AIDecompositionItem] = Field(description="A list of tasks decomposed from the requirements")

@router.post("/projects/{project_id}/ai/decompose", response_model=AIDecompositionResponse)
async def decompose_tasks(
    project_id: int,
    body: AIDecompositionRequest,
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
):
    # プロジェクトへのアクセス権限を確認
    _verify_project_access(project_id, current_user_id, session)

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )
        
        structured_llm = llm.with_structured_output(TaskList)
        
        prompt = f"""
        You are an expert project manager. 
        Decompose the following project requirements into a clear, actionable list of tasks.
        For each task, provide:
        - title: Concise task name
        - description: Brief explanation of what needs to be done
        - priority: 1 (Low), 2 (Medium), or 3 (High)
        - estimate: Estimated hours (float)

        Requirements:
        {body.prompt}
        """
        
        result = await structured_llm.ainvoke(prompt)
        
        # 生成されたタスクをDBに保存（バルクインサート的な処理）
        new_tasks = []
        for item in result.tasks:
            task = Task(
                project_id=project_id,
                sprint_id=body.sprint_id,
                title=item.title,
                description=item.description,
                priority=item.priority,
                estimate=item.estimate,
                status="todo",
            )
            session.add(task)
            new_tasks.append(task)
        
        session.commit()
        
        return AIDecompositionResponse(tasks=result.tasks)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI decomposition failed: {str(e)}"
        )
