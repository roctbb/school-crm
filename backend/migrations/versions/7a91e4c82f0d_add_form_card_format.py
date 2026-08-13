"""add form card format

Revision ID: 7a91e4c82f0d
Revises: c3a82d91f640
Create Date: 2026-08-13 17:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '7a91e4c82f0d'
down_revision = 'c3a82d91f640'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'forms',
        sa.Column('card_format', sa.String(length=32), server_default='default', nullable=False),
    )
    op.execute(
        "UPDATE forms SET card_format = 'session_results' "
        "WHERE lower(btrim(name)) = lower('Результаты сессии')"
    )


def downgrade():
    op.drop_column('forms', 'card_format')
