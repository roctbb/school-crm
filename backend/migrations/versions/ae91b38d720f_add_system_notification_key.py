"""Deduplicate internal notifications independently of OAuth clients.

Revision ID: ae91b38d720f
Revises: 8db3c921a047
"""
from alembic import op
import sqlalchemy as sa

revision = 'ae91b38d720f'
down_revision = '8db3c921a047'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('notifications', sa.Column('system_key', sa.String(128), nullable=True))
    op.create_unique_constraint('uq_notifications_system_key', 'notifications', ['system_key'])


def downgrade():
    op.drop_constraint('uq_notifications_system_key', 'notifications', type_='unique')
    op.drop_column('notifications', 'system_key')
