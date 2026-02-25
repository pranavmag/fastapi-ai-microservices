"""add ai_summary to note

Revision ID: a1b2c3d4e5f6
Revises: 020f74466067
Create Date: 2026-02-24

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '020f74466067'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('note', sa.Column('ai_summary', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('note', 'ai_summary')
