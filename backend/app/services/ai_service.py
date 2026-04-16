from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import json

class WorkflowState(TypedDict):
    """LangGraphワークフローの状態定義"""
    user_requirement: str
    epics: List[dict]
    tasks: List[dict]
    sprints: List[dict]
    error: Optional[str]


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


def extract_epics_node(state: WorkflowState) -> WorkflowState:
    """要件からエピック（大分類）を抽出"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    prompt = f"""
    以下のプロジェクト要件から、開発に必要な大分類（エピック）を抽出してください。
    各エピックには名前と簡単な説明を含めてください。
    JSON形式で出力すること。
    
    要件:
    {state['user_requirement']}
    
    出力形式:
    [
      {{"name": "エピック名", "description": "エピックの説明"}},
      ...
    ]
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        # JSON部分を抽出（LLMが余分なテキストを含む場合があるため）
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        epics = json.loads(content)
        state["epics"] = epics
        state["error"] = None
        
    except Exception as e:
        state["error"] = f"エピック抽出エラー: {str(e)}"
        state["epics"] = []
    
    return state


def decompose_tasks_node(state: WorkflowState) -> WorkflowState:
    """エピックを詳細タスクに分解"""
    if not state["epics"]:
        state["error"] = "エピックが抽出されていません"
        return state
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    epics_json = json.dumps(state["epics"], ensure_ascii=False)
    
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
    
    出力形式:
    [
      {{"title": "タスク名", "description": "説明", "priority": 2, "estimate": 8.0, "epic": "エピック名"}},
      ...
    ]
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        # JSON部分を抽出
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        tasks = json.loads(content)
        state["tasks"] = tasks
        state["error"] = None
        
    except Exception as e:
        state["error"] = f"タスク分解エラー: {str(e)}"
        state["tasks"] = []
    
    return state


def plan_sprints_node(state: WorkflowState) -> WorkflowState:
    """タスクをスプリントに割り振る"""
    if not state["tasks"]:
        state["error"] = "タスクが分解されていません"
        return state
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    tasks_json = json.dumps(state["tasks"], ensure_ascii=False)
    
    prompt = f"""
    以下のタスクを論理的なスプリント（2週間単位）に割り振ってください。
    各スプリントには以下の情報を含めてください:
    - name: スプリント名 (例: "Sprint 1")
    - tasks: 割り当てられたタスクのインデックスリスト
    - total_estimate: 合計推定工数
    
    タスク一覧:
    {tasks_json}
    
    出力形式:
    [
      {{"name": "Sprint 1", "tasks": [0, 1, 2], "total_estimate": 24.0}},
      {{"name": "Sprint 2", "tasks": [3, 4, 5], "total_estimate": 32.0}},
      ...
    ]
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        # JSON部分を抽出
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        sprints = json.loads(content)
        state["sprints"] = sprints
        state["error"] = None
        
    except Exception as e:
        state["error"] = f"スプリント計画エラー: {str(e)}"
        state["sprints"] = []
    
    return state


async def run_ai_decomposition(user_requirement: str) -> dict:
    """
    AIワークフローを実行するメイン関数
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