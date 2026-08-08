"""add OpenID Connect provider

Revision ID: e3b4c7d91a20
Revises: d8f12a4c9b01
Create Date: 2026-08-08 14:30:00.000000

"""
import uuid

from alembic import op
import sqlalchemy as sa


revision = 'e3b4c7d91a20'
down_revision = 'd8f12a4c9b01'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('sso_subject', sa.String(length=36), nullable=True))

    connection = op.get_bind()
    user_ids = connection.execute(sa.text('SELECT id FROM users')).scalars().all()
    for user_id in user_ids:
        connection.execute(
            sa.text('UPDATE users SET sso_subject = :subject WHERE id = :user_id'),
            {'subject': str(uuid.uuid4()), 'user_id': user_id},
        )

    op.alter_column('users', 'sso_subject', nullable=False)
    op.create_unique_constraint('uq_users_sso_subject', 'users', ['sso_subject'])

    op.create_table(
        'oauth_clients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.String(length=120), nullable=False),
        sa.Column('client_secret_hash', sa.String(length=256), nullable=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('redirect_uris', sa.JSON(), server_default=sa.text("'[]'::json"), nullable=False),
        sa.Column(
            'post_logout_redirect_uris', sa.JSON(), server_default=sa.text("'[]'::json"), nullable=False
        ),
        sa.Column(
            'allowed_scopes', sa.JSON(),
            server_default=sa.text("'[\"openid\", \"profile\", \"email\", \"roles\"]'::json"),
            nullable=False,
        ),
        sa.Column(
            'allowed_roles', sa.JSON(),
            server_default=sa.text("'[\"student\", \"teacher\", \"admin\"]'::json"),
            nullable=False,
        ),
        sa.Column('is_confidential', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id', name='uq_oauth_clients_client_id'),
    )

    op.create_table(
        'oauth_authorization_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code_hash', sa.String(length=64), nullable=False),
        sa.Column('client_id', sa.String(length=120), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('redirect_uri', sa.Text(), nullable=False),
        sa.Column('scope', sa.Text(), nullable=False),
        sa.Column('nonce', sa.String(length=255), nullable=False),
        sa.Column('code_challenge', sa.String(length=128), nullable=False),
        sa.Column('code_challenge_method', sa.String(length=10), server_default='S256', nullable=False),
        sa.Column('auth_time', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['oauth_clients.client_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code_hash', name='uq_oauth_authorization_codes_code_hash'),
    )
    op.create_table(
        'oauth_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.String(length=120), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('access_token_hash', sa.String(length=64), nullable=False),
        sa.Column('refresh_token_hash', sa.String(length=64), nullable=True),
        sa.Column('token_type', sa.String(length=40), server_default='Bearer', nullable=False),
        sa.Column('scope', sa.Text(), nullable=False),
        sa.Column('issued_at', sa.Integer(), nullable=False),
        sa.Column('expires_in', sa.Integer(), nullable=False),
        sa.Column('refresh_expires_at', sa.Integer(), nullable=True),
        sa.Column('access_token_revoked_at', sa.Integer(), server_default='0', nullable=False),
        sa.Column('refresh_token_revoked_at', sa.Integer(), server_default='0', nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['oauth_clients.client_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('access_token_hash', name='uq_oauth_tokens_access_token_hash'),
        sa.UniqueConstraint('refresh_token_hash', name='uq_oauth_tokens_refresh_token_hash'),
    )

def downgrade():
    op.drop_table('oauth_tokens')
    op.drop_table('oauth_authorization_codes')
    op.drop_table('oauth_clients')
    op.drop_constraint('uq_users_sso_subject', 'users', type_='unique')
    op.drop_column('users', 'sso_subject')
