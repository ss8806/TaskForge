"""AIサービスのテスト。"""

import pytest
from unittest.mock import MagicMock, patch

from app.services.ai_service import (
    EpicList,
    SprintPlanList,
    TaskList,
    decompose_tasks_node,
    extract_epics_node,
    plan_sprints_node,
)


class TestEpicList:
    """EpicList モデルのテスト"""

    def test_from_json_valid(self):
        """有効なJSONからのパース"""
        json_str = '{"epics": [{"name": "Auth", "description": "認証機能"}]}'
        result = EpicList.from_json(json_str)
        
        assert len(result.epics) == 1
        assert result.epics[0].name == "Auth"
        assert result.epics[0].description == "認証機能"

    def test_from_json_multiple(self):
        """複数のエピックのパース"""
        json_str = """
        {
            "epics": [
                {"name": "Auth", "description": "認証機能"},
                {"name": "API", "description": "API実装"}
            ]
        }
        """
        result = EpicList.from_json(json_str)
        
        assert len(result.epics) == 2
        assert result.epics[0].name == "Auth"
        assert result.epics[1].name == "API"


class TestTaskList:
    """TaskList モデルのテスト"""

    def test_from_json_valid(self):
        """有効なJSONからのパース"""
        json_str = """
        {
            "tasks": [
                {
                    "title": "Login Feature",
                    "description": "Implement login",
                    "priority": 2,
                    "estimate": 8.0,
                    "epic": "Auth"
                }
            ]
        }
        """
        result = TaskList.from_json(json_str)
        
        assert len(result.tasks) == 1
        assert result.tasks[0].title == "Login Feature"
        assert result.tasks[0].priority == 2
        assert result.tasks[0].estimate == 8.0


class TestSprintPlanList:
    """SprintPlanList モデルのテスト"""

    def test_from_json_valid(self):
        """有効なJSONからのパース"""
        json_str = """
        {
            "sprints": [
                {"name": "Sprint 1", "tasks": [0, 1], "total_estimate": 16.0}
            ]
        }
        """
        result = SprintPlanList.from_json(json_str)
        
        assert len(result.sprints) == 1
        assert result.sprints[0].name == "Sprint 1"
        assert result.sprints[0].tasks == [0, 1]


class TestExtractEpicsNode:
    """extract_epics_node のテスト"""

    @patch("app.services.ai_service.get_llm")
    def test_extract_epics_success(self, mock_get_llm):
        """エピック抽出の成功ケース"""
        # モックの設定
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"epics": [{"name": "Auth", "description": "認証"}]}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "user_requirement": "認証機能を実装してください",
            "epics": [],
            "tasks": [],
            "sprints": [],
            "error": None,
        }

        result = extract_epics_node(state)

        assert result["error"] is None
        assert len(result["epics"]) == 1
        assert result["epics"][0]["name"] == "Auth"
        mock_llm.invoke.assert_called_once()

    @patch("app.services.ai_service.get_llm")
    def test_extract_epics_failure(self, mock_get_llm):
        """エピック抽出の失敗ケース"""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("API Error")
        mock_get_llm.return_value = mock_llm

        state = {
            "user_requirement": "テスト要件",
            "epics": [],
            "tasks": [],
            "sprints": [],
            "error": None,
        }

        result = extract_epics_node(state)

        assert result["error"] is not None
        assert "エピック抽出エラー" in result["error"]
        assert result["epics"] == []


class TestDecomposeTasksNode:
    """decompose_tasks_node のテスト"""

    @patch("app.services.ai_service.get_llm")
    def test_decompose_tasks_success(self, mock_get_llm):
        """タスク分解の成功ケース"""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = """
        {
            "tasks": [
                {
                    "title": "Login",
                    "description": "Implement login",
                    "priority": 2,
                    "estimate": 8.0,
                    "epic": "Auth"
                }
            ]
        }
        """
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "user_requirement": "テスト",
            "epics": [{"name": "Auth", "description": "認証"}],
            "tasks": [],
            "sprints": [],
            "error": None,
        }

        result = decompose_tasks_node(state)

        assert result["error"] is None
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["title"] == "Login"

    def test_decompose_tasks_no_epics(self):
        """エピックなしの場合"""
        state = {
            "user_requirement": "テスト",
            "epics": [],
            "tasks": [],
            "sprints": [],
            "error": None,
        }

        result = decompose_tasks_node(state)

        assert result["error"] == "エピックが抽出されていません"
        assert result["tasks"] == []


class TestPlanSprintsNode:
    """plan_sprints_node のテスト"""

    @patch("app.services.ai_service.get_llm")
    def test_plan_sprints_success(self, mock_get_llm):
        """スプリント計画の成功ケース"""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = """
        {
            "sprints": [
                {"name": "Sprint 1", "tasks": [0, 1], "total_estimate": 16.0}
            ]
        }
        """
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        state = {
            "user_requirement": "テスト",
            "epics": [],
            "tasks": [
                {"title": "Task 1", "estimate": 8.0},
                {"title": "Task 2", "estimate": 8.0},
            ],
            "sprints": [],
            "error": None,
        }

        result = plan_sprints_node(state)

        assert result["error"] is None
        assert len(result["sprints"]) == 1

    def test_plan_sprints_no_tasks(self):
        """タスクなしの場合"""
        state = {
            "user_requirement": "テスト",
            "epics": [],
            "tasks": [],
            "sprints": [],
            "error": None,
        }

        result = plan_sprints_node(state)

        assert result["error"] == "タスクが分解されていません"
        assert result["sprints"] == []

