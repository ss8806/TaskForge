"""テストデータ生成ファクトリ。"""

import factory

from app.models import Project, Sprint, Task, User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Userモデルのテストデータファクトリ。"""

    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # testpassword123
    role = "user"
    total_points = 0


class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Projectモデルのテストデータファクトリ。"""

    class Meta:
        model = Project
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Project {n}")
    description = factory.Faker("text", max_nb_chars=200)
    owner = factory.SubFactory(UserFactory)


class SprintFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Sprintモデルのテストデータファクトリ。"""

    class Meta:
        model = Sprint
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Sprint {n}")
    start_date = factory.Faker("date_between", start_date="-30d", end_date="today")
    end_date = factory.Faker("date_between", start_date="today", end_date="+30d")
    project = factory.SubFactory(ProjectFactory)


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Taskモデルのテストデータファクトリ。"""

    class Meta:
        model = Task
        sqlalchemy_session_persistence = "commit"

    title = factory.Sequence(lambda n: f"Task {n}")
    description = factory.Faker("text", max_nb_chars=500)
    status = "todo"
    priority = 2
    sprint = factory.SubFactory(SprintFactory)
