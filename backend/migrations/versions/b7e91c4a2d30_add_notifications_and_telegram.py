"""add notifications and Telegram integration

Revision ID: b7e91c4a2d30
Revises: 4ad8f22c1b7e
Create Date: 2026-08-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b7e91c4a2d30'
down_revision = '4ad8f22c1b7e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'oauth_clients',
        sa.Column('can_send_notifications', sa.Boolean(), server_default=sa.false(), nullable=False),
    )

    op.create_table(
        'telegram_connections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('linked_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chat_id', name='uq_telegram_connections_chat_id'),
        sa.UniqueConstraint('user_id', name='uq_telegram_connections_user_id'),
    )
    op.create_table(
        'telegram_link_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash', name='uq_telegram_link_tokens_token_hash'),
    )
    op.create_index('ix_telegram_link_tokens_user_id', 'telegram_link_tokens', ['user_id'])
    op.create_index('ix_telegram_link_tokens_expires_at', 'telegram_link_tokens', ['expires_at'])

    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('source_client_id', sa.String(length=120), nullable=True),
        sa.Column('source_name', sa.String(length=120), nullable=False),
        sa.Column('idempotency_key', sa.String(length=128), nullable=True),
        sa.Column('payload_hash', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('email_sent_at', sa.DateTime(), nullable=True),
        sa.Column('telegram_sent_at', sa.DateTime(), nullable=True),
        sa.Column('email_error', sa.Text(), nullable=True),
        sa.Column('telegram_error', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['source_client_id'], ['oauth_clients.client_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'source_client_id', 'idempotency_key', name='uq_notifications_client_idempotency'
        ),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])


def downgrade():
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')
    op.drop_index('ix_telegram_link_tokens_expires_at', table_name='telegram_link_tokens')
    op.drop_index('ix_telegram_link_tokens_user_id', table_name='telegram_link_tokens')
    op.drop_table('telegram_link_tokens')
    op.drop_table('telegram_connections')
    op.drop_column('oauth_clients', 'can_send_notifications')
