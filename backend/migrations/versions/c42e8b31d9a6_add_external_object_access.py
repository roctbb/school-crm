"""Allow external clients to read explicitly selected object types.

Revision ID: c42e8b31d9a6
Revises: a10710c0de01
"""
from alembic import op
import sqlalchemy as sa

revision = 'c42e8b31d9a6'
down_revision = 'a10710c0de01'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('oauth_clients', sa.Column(
        'allowed_object_types', sa.JSON(), nullable=False,
        server_default=sa.text("'[]'::json"),
    ))


def downgrade():
    op.drop_column('oauth_clients', 'allowed_object_types')
