"""
リポジトリ分析サービス
コードベースの構造、技術スタック、既存機能などを解析する
"""

import contextlib
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# 解析対象外ディレクトリ
EXCLUDED_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    ".output",
    ".turbo",
}

# 解析対象外ファイル
EXCLUDED_FILE_EXTS = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".dylib",
    ".db",
    ".sqlite",
    ".lock",
    ".min.js",
    ".min.css",
}

# テクノロジー検出パターン
TECH_PATTERNS = {
    "Python": ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "Pipfile"],
    "FastAPI": ["fastapi"],
    "Django": ["django", "manage.py"],
    "Flask": ["flask"],
    "SQLAlchemy": ["sqlalchemy", "sqlmodel"],
    "Node.js": ["package.json"],
    "React": ["react", "next.config"],
    "Next.js": ["next.config", "next"],
    "Vue.js": ["vue", "nuxt.config"],
    "TypeScript": ["tsconfig.json", ".ts"],
    "Tailwind CSS": ["tailwind.config"],
    "PostgreSQL": ["postgresql", "psycopg"],
    "MySQL": ["mysql", "pymysql", "mysqlclient"],
    "Redis": ["redis"],
    "Docker": ["Dockerfile", "docker-compose"],
    "Alembic": ["alembic.ini", "alembic"],
    "Celery": ["celery"],
    "LangChain": ["langchain", "langgraph"],
    "OpenAI": ["openai"],
    "Pytest": ["pytest.ini", "pyproject.toml"],
    "Vite": ["vite.config"],
    "Webpack": ["webpack.config"],
}

# APIエンドポイント検出パターン（Python）
API_PATTERNS = [
    # FastAPI
    r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
    r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
    # Flask
    r'@app\.route\s*\(\s*["\']([^"\']+)["\']',
]

# DBモデル検出パターン
MODEL_PATTERNS = [
    # SQLModel
    r'class\s+(\w+)\s*\(\s*SQLModel\s*,\s*table\s*=\s*True\s*\)',
    # SQLAlchemy
    r'class\s+(\w+)\s*\(\s*Base\s*\)',
    r'class\s+(\w+)\s*\(\s*db\.Model\s*\)',
]


class RepositoryAnalyzer:
    """リポジトリ分析サービス"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise FileNotFoundError(f"リポジトリパスが存在しません: {repo_path}")
        if not self.repo_path.is_dir():
            raise NotADirectoryError(f"ディレクトリではありません: {repo_path}")

    def analyze(self) -> dict[str, Any]:
        """リポジトリを包括的に分析"""
        return {
            "structure": self._analyze_structure(),
            "tech_stack": self._detect_tech_stack(),
            "api_endpoints": self._extract_api_endpoints(),
            "database_models": self._extract_db_models(),
            "existing_features": self._identify_features(),
        }

    def _analyze_structure(self) -> dict[str, Any]:
        """ディレクトリ構造を解析"""
        structure: dict[str, Any] = {
            "root_dirs": [],
            "file_count": 0,
            "total_size_bytes": 0,
        }

        file_count = 0
        total_size = 0

        for root, _dirs, files in self._walk_with_ignore():
            # ルート直下のディレクトリを取得
            rel_path = Path(root).relative_to(self.repo_path)
            if len(rel_path.parts) == 1:
                structure["root_dirs"].append(rel_path.name)

            for f in files:
                file_count += 1
                with contextlib.suppress(OSError):
                    total_size += (Path(root) / f).stat().st_size

        structure["file_count"] = file_count
        structure["total_size_bytes"] = total_size

        return structure

    def _detect_tech_stack(self) -> list[str]:
        """使用技術スタックを検出"""
        tech_stack: list[str] = []

        # ファイル名ベースの検出
        for tech, patterns in TECH_PATTERNS.items():
            # 特殊パターン処理
            if tech == "TypeScript":
                # .tsファイルが存在するかチェック
                for _, _, files in self._walk_with_ignore():
                    if any(f.endswith(".ts") or f.endswith(".tsx") for f in files):
                        tech_stack.append(tech)
                        break
                continue

            for pattern in patterns:
                if (self.repo_path / pattern).exists():
                    if tech not in tech_stack:
                        tech_stack.append(tech)
                    break

        # ファイル内容ベースの検出
        # package.json の dependencies 確認
        pkg_json = self.repo_path / "package.json"
        if pkg_json.exists():
            try:
                import json

                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                deps = {
                    **data.get("dependencies", {}),
                    **data.get("devDependencies", {}),
                }
                dep_keys = " ".join(deps.keys())

                if "react" in dep_keys.lower() and "React" not in tech_stack:
                    tech_stack.append("React")
                if "vue" in dep_keys.lower() and "Vue.js" not in tech_stack:
                    tech_stack.append("Vue.js")
                if "next" in dep_keys.lower() and "Next.js" not in tech_stack:
                    tech_stack.append("Next.js")
                if "tailwindcss" in dep_keys.lower() and "Tailwind CSS" not in tech_stack:
                    tech_stack.append("Tailwind CSS")
            except Exception:
                pass

        # pyproject.toml / requirements.txt の内容確認
        for req_file in ["pyproject.toml", "requirements.txt"]:
            req_path = self.repo_path / req_file
            if req_path.exists():
                try:
                    content = req_path.read_text(encoding="utf-8").lower()
                    if "fastapi" in content and "FastAPI" not in tech_stack:
                        tech_stack.append("FastAPI")
                    if "sqlmodel" in content and "SQLAlchemy" not in tech_stack:
                        tech_stack.append("SQLAlchemy")
                    if ("langchain" in content or "langgraph" in content) and "LangChain" not in tech_stack:
                        tech_stack.append("LangChain")
                    if "celery" in content and "Celery" not in tech_stack:
                        tech_stack.append("Celery")
                except Exception:
                    pass

        return sorted(tech_stack)

    def _extract_api_endpoints(self) -> list[dict[str, str]]:
        """APIエンドポイントを抽出"""
        endpoints: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()

        # Pythonファイルを検索
        for root, _, files in self._walk_with_ignore():
            for f in files:
                if not f.endswith(".py"):
                    continue

                file_path = Path(root) / f
                try:
                    content = file_path.read_text(encoding="utf-8")
                    for pattern in API_PATTERNS:
                        for match in re.finditer(pattern, content):
                            groups = match.groups()
                            if len(groups) == 2:
                                method, path = groups
                            else:
                                method = "GET"
                                path = groups[0]

                            key = (method.upper(), path)
                            if key not in seen:
                                seen.add(key)
                                endpoints.append(
                                    {
                                        "method": method.upper(),
                                        "path": path,
                                        "file": str(file_path.relative_to(self.repo_path)),
                                    }
                                )
                except Exception:
                    continue

        return endpoints

    def _extract_db_models(self) -> list[dict[str, str]]:
        """データベースモデルを抽出"""
        models: list[dict[str, str]] = []

        for root, _, files in self._walk_with_ignore():
            for f in files:
                if not f.endswith(".py"):
                    continue

                file_path = Path(root) / f
                try:
                    content = file_path.read_text(encoding="utf-8")
                    for pattern in MODEL_PATTERNS:
                        for match in re.finditer(pattern, content):
                            model_name = match.group(1)
                            # 一般的なベースクラス名は除外
                            if model_name in {"Base", "Model"}:
                                continue
                            models.append(
                                {
                                    "name": model_name,
                                    "file": str(file_path.relative_to(self.repo_path)),
                                }
                            )
                except Exception:
                    continue

        return models

    def _identify_features(self) -> list[str]:
        """既存機能を特定"""
        features: list[str] = []

        # ルートディレクトリの確認
        for item in self.repo_path.iterdir():
            if item.is_dir() and item.name not in EXCLUDED_DIRS:
                # 一般的な機能ディレクトリ名から推測
                name = item.name.lower()
                feature_map = {
                    "auth": "認証機能",
                    "user": "ユーザー管理",
                    "task": "タスク管理",
                    "project": "プロジェクト管理",
                    "sprint": "スプリント管理",
                    "api": "API機能",
                    "admin": "管理機能",
                    "report": "レポート機能",
                    "notification": "通知機能",
                    "search": "検索機能",
                    "upload": "ファイルアップロード",
                    "payment": "決済機能",
                    "billing": "請求機能",
                }
                for key, feature in feature_map.items():
                    if key in name:
                        features.append(feature)

        # routerファイルから機能推測
        routers_dir = self.repo_path / "app" / "api" / "routers"
        if routers_dir.exists():
            for f in routers_dir.glob("*.py"):
                if f.name == "__init__.py":
                    continue
                feature_name = f.stem.replace("_", " ").title()
                features.append(f"{feature_name}機能")

        # servicesディレクトリから機能推測
        services_dir = self.repo_path / "app" / "services"
        if services_dir.exists():
            for f in services_dir.glob("*.py"):
                if f.name == "__init__.py":
                    continue
                feature_name = f.stem.replace("_", " ").title()
                features.append(f"{feature_name}サービス")

        return list(set(features))

    def _walk_with_ignore(self):
        """除外ディレクトリを無視してwalk"""
        for root, dirs, files in self.repo_path.walk(top_down=True):
            # 除外ディレクトリをin-placeでフィルタ
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            # 除外ファイルをフィルタ
            files = [f for f in files if Path(f).suffix not in EXCLUDED_FILE_EXTS]
            yield str(root), dirs, files
