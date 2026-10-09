"""Add visibility independently of approval and deletion.

Revision ID: a10710c0de01
Revises: f6b7c8d9e012
"""
from alembic import op
import sqlalchemy as sa

revision = 'a10710c0de01'
down_revision = 'f6b7c8d9e012'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('objects', sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    op.drop_column('objects', 'is_hidden')
