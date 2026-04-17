"""add_soft_delete_columns

Revision ID: 60aabd7adfb5
Revises: ef5b857ce607
Create Date: 2026-04-17 15:33:21.163151

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "60aabd7adfb5"
down_revision: str | Sequence[str] | None = "ef5b857ce607"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add deleted_at column to user table
    op.add_column("user", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.create_index(op.f("ix_user_deleted_at"), "user", ["deleted_at"], unique=False)

    # Add deleted_at column to project table
    op.add_column("project", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.create_index(
        op.f("ix_project_deleted_at"), "project", ["deleted_at"], unique=False
    )

    # Add deleted_at column to sprint table
    op.add_column("sprint", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.create_index(
        op.f("ix_sprint_deleted_at"), "sprint", ["deleted_at"], unique=False
    )

    # Add deleted_at column to task table
    op.add_column("task", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.create_index(op.f("ix_task_deleted_at"), "task", ["deleted_at"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove deleted_at column from task table
    op.drop_index(op.f("ix_task_deleted_at"), table_name="task")
    op.drop_column("task", "deleted_at")

    # Remove deleted_at column from sprint table
    op.drop_index(op.f("ix_sprint_deleted_at"), table_name="sprint")
    op.drop_column("sprint", "deleted_at")

    # Remove deleted_at column from project table
    op.drop_index(op.f("ix_project_deleted_at"), table_name="project")
    op.drop_column("project", "deleted_at")

    # Remove deleted_at column from user table
    op.drop_index(op.f("ix_user_deleted_at"), table_name="user")
    op.drop_column("user", "deleted_at")
