"""
AIタスク分解サービス
LangGraph + OpenAI Structured Outputs を使用
"""

from typing import TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

# ============================================================
# Pydantic Models for Structured Output
# ============================================================


class Epic(BaseModel):
    """エピック（大分類）"""

    name: str = Field(description="エピック名")
    description: str = Field(description="エピックの説明")


class EpicList(BaseModel):
    """エピック一覧"""

    epics: list[Epic] = Field(description="抽出されたエピック一覧")


class TaskItem(BaseModel):
    """タスク項目"""

    title: str = Field(description="タスク名")
    description: str = Field(description="タスクの説明", default="")
    priority: int = Field(
        description="優先度 (1=低, 2=中, 3=高)", ge=1, le=3, default=2
    )
    estimate: float = Field(description="推定工数（時間）", default=8.0)
    epic: str = Field(description="所属エピック名")


class TaskList(BaseModel):
    """タスク一覧"""

    tasks: list[TaskItem] = Field(description="分解されたタスク一覧")


class SprintPlan(BaseModel):
    """スプリント計画"""

    name: str = Field(description="スプリント名")
    tasks: list[int] = Field(description="割り当てられたタスクのインデックスリスト")
    total_estimate: float = Field(description="合計推定工数")


class SprintPlanList(BaseModel):
    """スプリント計画一覧"""

    sprints: list[SprintPlan] = Field(description="計画されたスプリント一覧")


# ============================================================
# Workflow State
# ============================================================


class WorkflowState(TypedDict):
    """LangGraphワークフローの状態定義"""

    user_requirement: str
    epics: list[dict]
    tasks: list[dict]
    sprints: list[dict]
    error: str | None


# ============================================================
# LLM Initialization
# ============================================================


def get_llm():
    """LLMインスタンスを取得（OpenAI互換API）"""
    from app.core.config import settings
    
    return ChatOpenAI(
        model=settings.AI_MODEL,
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_API_BASE,
    )


# ============================================================
# Workflow Nodes
# ============================================================


def extract_epics_node(state: WorkflowState) -> WorkflowState:
    """要件からエピック（大分類）を抽出 - 構造化出力使用"""
    llm = get_llm()
    structured_llm = llm.with_structured_output(EpicList)

    prompt = f"""
    以下のプロジェクト要件から、開発に必要な大分類（エピック）を抽出してください。
    各エピックには名前と簡単な説明を含めてください。
    
    要件:
    {state["user_requirement"]}
    """

    try:
        result: EpicList = structured_llm.invoke([HumanMessage(content=prompt)])
        state["epics"] = [epic.model_dump() for epic in result.epics]
        state["error"] = None

    except Exception as e:
        state["error"] = f"エピック抽出エラー: {str(e)}"
        state["epics"] = []

    return state


def decompose_tasks_node(state: WorkflowState) -> WorkflowState:
    """エピックを詳細タスクに分解 - 構造化出力使用"""
    if not state["epics"]:
        state["error"] = "エピックが抽出されていません"
        return state

    import json

    llm = get_llm()
    structured_llm = llm.with_structured_output(TaskList)

    epics_json = json.dumps(state["epics"], ensure_ascii=False, indent=2)

    prompt = f"""
    以下のエピックを詳細なタスクに分解してください。
    各タスクには以下の情報を含めてください:
    - title: タスク名
    - description: タスクの説明
    - priority: 優先度 (1=低, 2=中, 3=高)
    - estimate: 推定工数（時間）
    - epic: 所属エピック名
    
    エピック一覧:
    {epics_json}
    """

    try:
        result: TaskList = structured_llm.invoke([HumanMessage(content=prompt)])
        state["tasks"] = [task.model_dump() for task in result.tasks]
        state["error"] = None

    except Exception as e:
        state["error"] = f"タスク分解エラー: {str(e)}"
        state["tasks"] = []

    return state


def plan_sprints_node(state: WorkflowState) -> WorkflowState:
    """タスクをスプリントに割り振る - 構造化出力使用"""
    if not state["tasks"]:
        state["error"] = "タスクが分解されていません"
        return state

    import json

    llm = get_llm()
    structured_llm = llm.with_structured_output(SprintPlanList)

    tasks_json = json.dumps(state["tasks"], ensure_ascii=False, indent=2)

    prompt = f"""
    以下のタスクを論理的なスプリント（2週間単位）に割り振ってください。
    各スプリントには以下の情報を含めてください:
    - name: スプリント名 (例: "Sprint 1")
    - tasks: 割り当てられたタスクのインデックスリスト（0始まり）
    - total_estimate: 合計推定工数
    
    1スプリントあたりの理想的な工数は80時間程度です。
    依存関係のあるタスクは同じスプリントにまとめてください。
    
    タスク一覧:
    {tasks_json}
    """

    try:
        result: SprintPlanList = structured_llm.invoke([HumanMessage(content=prompt)])
        state["sprints"] = [sprint.model_dump() for sprint in result.sprints]
        state["error"] = None

    except Exception as e:
        state["error"] = f"スプリント計画エラー: {str(e)}"
        state["sprints"] = []

    return state


# ============================================================
# Workflow Creation
# ============================================================


def create_ai_workflow() -> StateGraph:
    """
    AIタスク分解ワークフローを作成
    3段階の処理: エピック抽出 → タスク分解 → スプリント計画
    """
    workflow = StateGraph(WorkflowState)

    # ノード定義
    workflow.add_node("extract_epics", extract_epics_node)
    workflow.add_node("decompose_tasks", decompose_tasks_node)
    workflow.add_node("plan_sprints", plan_sprints_node)

    # エッジ設定
    workflow.set_entry_point("extract_epics")
    workflow.add_edge("extract_epics", "decompose_tasks")
    workflow.add_edge("decompose_tasks", "plan_sprints")
    workflow.add_edge("plan_sprints", END)

    return workflow.compile()


# ============================================================
# Main Entry Point
# ============================================================


async def run_ai_decomposition(user_requirement: str) -> dict:
    """
    AIワークフローを実行するメイン関数

    Args:
        user_requirement: ユーザーからの要件入力

    Returns:
        dict: {
            "epics": List[dict],  # 抽出されたエピック
            "tasks": List[dict],  # 分解されたタスク
            "sprints": List[dict],  # 計画されたスプリント
            "error": Optional[str]  # エラーメッセージ
        }
    """
    workflow = create_ai_workflow()

    initial_state: WorkflowState = {
        "user_requirement": user_requirement,
        "epics": [],
        "tasks": [],
        "sprints": [],
        "error": None,
    }

    result = workflow.invoke(initial_state)

    return {
        "epics": result["epics"],
        "tasks": result["tasks"],
        "sprints": result["sprints"],
        "error": result["error"],
    }
