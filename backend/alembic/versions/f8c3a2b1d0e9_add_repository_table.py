"""add_repository_table

Revision ID: f8c3a2b1d0e9
Revises: 1e22211c0b09
Create Date: 2026-04-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f8c3a2b1d0e9'
down_revision: Union[str, Sequence[str], None] = '1e22211c0b09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create repository table
    op.create_table(
        'repository',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('repo_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='github'),
        sa.Column('branch', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='main'),
        sa.Column('analysis_result', sa.JSON(), nullable=True),
        sa.Column('last_analyzed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id'),
    )
    # Create index on project_id for faster lookups
    op.create_index('ix_repository_project_id', 'repository', ['project_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_repository_project_id', table_name='repository')
    op.drop_table('repository')
