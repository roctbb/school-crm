"""add remembered OAuth consents

Revision ID: 4ad8f22c1b7e
Revises: e3b4c7d91a20
Create Date: 2026-08-08 16:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '4ad8f22c1b7e'
down_revision = 'e3b4c7d91a20'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'oauth_consents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.String(length=120), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('scopes', sa.JSON(), server_default=sa.text("'[]'::json"), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['oauth_clients.client_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'client_id', name='uq_oauth_consents_user_client'),
    )
    op.create_index('ix_oauth_consents_client_id', 'oauth_consents', ['client_id'], unique=False)
    op.create_index('ix_oauth_consents_user_id', 'oauth_consents', ['user_id'], unique=False)


def downgrade():
    op.drop_index('ix_oauth_consents_user_id', table_name='oauth_consents')
    op.drop_index('ix_oauth_consents_client_id', table_name='oauth_consents')
    op.drop_table('oauth_consents')
