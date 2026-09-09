"""Add the shared birthday display link.

Revision ID: 8db3c921a047
Revises: 3f6b1d9a0c42
"""
from alembic import op
import sqlalchemy as sa

revision = '8db3c921a047'
down_revision = '3f6b1d9a0c42'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'birthday_display',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(64), nullable=True),
    )


def downgrade():
    op.drop_table('birthday_display')
