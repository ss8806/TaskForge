"""add achievement key and title fields

Revision ID: 1e22211c0b09
Revises: 88e5fcd2b3a5
Create Date: 2026-04-19 19:45:13.877812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '1e22211c0b09'
down_revision: Union[str, Sequence[str], None] = '88e5fcd2b3a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # achievement テーブルに key と title カラムを追加
    op.add_column('achievement', sa.Column('key', sa.String(), nullable=False, server_default=''))
    op.add_column('achievement', sa.Column('title', sa.String(), nullable=False, server_default=''))
    
    # key カラムにユニークインデックスを作成
    op.create_index(op.f('ix_achievement_key'), 'achievement', ['key'], unique=True)
    
    # 既存のレコードの key と title を name から設定
    # NOTE: 本番環境では、既存データに基づいて適切な値を設定する必要があります
    op.execute("""
        UPDATE achievement 
        SET key = LOWER(REPLACE(name, ' ', '_')), 
            title = name
        WHERE key = ''
    """)
    
    # server_default を削除（必須カラムなので）
    op.alter_column('achievement', 'key', server_default=None)
    op.alter_column('achievement', 'title', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    # インデックスを削除
    op.drop_index(op.f('ix_achievement_key'), table_name='achievement')
    
    # カラムを削除
    op.drop_column('achievement', 'title')
    op.drop_column('achievement', 'key')
