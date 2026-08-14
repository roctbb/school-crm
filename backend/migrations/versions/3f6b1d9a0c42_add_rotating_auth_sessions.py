"""add rotating auth sessions

Revision ID: 3f6b1d9a0c42
Revises: 7a91e4c82f0d
Create Date: 2026-08-14 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '3f6b1d9a0c42'
down_revision = '7a91e4c82f0d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'auth_refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('jti', sa.String(length=36), nullable=False),
        sa.Column('family_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('replaced_by_jti', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('jti', name='uq_auth_refresh_tokens_jti'),
    )
    op.create_index('ix_auth_refresh_tokens_family_id', 'auth_refresh_tokens', ['family_id'])
    op.create_index('ix_auth_refresh_tokens_user_id', 'auth_refresh_tokens', ['user_id'])
    op.create_index('ix_auth_refresh_tokens_expires_at', 'auth_refresh_tokens', ['expires_at'])


def downgrade():
    op.drop_index('ix_auth_refresh_tokens_expires_at', table_name='auth_refresh_tokens')
    op.drop_index('ix_auth_refresh_tokens_user_id', table_name='auth_refresh_tokens')
    op.drop_index('ix_auth_refresh_tokens_family_id', table_name='auth_refresh_tokens')
    op.drop_table('auth_refresh_tokens')
