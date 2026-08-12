"""move OIDC identity from users to CRM objects

Revision ID: c3a82d91f640
Revises: b7e91c4a2d30
Create Date: 2026-08-12 16:00:00.000000

"""
import uuid
from collections import defaultdict

from alembic import op
import sqlalchemy as sa


revision = 'c3a82d91f640'
down_revision = 'b7e91c4a2d30'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('objects', sa.Column('sso_subject', sa.String(length=36), nullable=True))

    connection = op.get_bind()
    object_ids = connection.execute(sa.text('SELECT id FROM objects')).scalars().all()
    for object_id in object_ids:
        connection.execute(
            sa.text('UPDATE objects SET sso_subject = :subject WHERE id = :object_id'),
            {'subject': str(uuid.uuid4()), 'object_id': object_id},
        )

    op.create_table(
        'user_identity_objects',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['object_id'], ['objects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('object_id', name='uq_user_identity_objects_object_id'),
    )

    invitation_links = connection.execute(sa.text(
        """
        SELECT user_id, object_id
        FROM invitations
        WHERE user_id IS NOT NULL AND object_id IS NOT NULL
        ORDER BY id DESC
        """
    )).all()
    objects_by_user = defaultdict(set)
    users_by_object = defaultdict(set)
    for user_id, object_id in invitation_links:
        objects_by_user[user_id].add(object_id)
        users_by_object[object_id].add(user_id)

    assigned_users = set()
    assigned_objects = set()

    def assign_identity(user_id, object_id):
        account_subject = connection.execute(
            sa.text('SELECT sso_subject FROM users WHERE id = :user_id'),
            {'user_id': user_id},
        ).scalar_one()
        connection.execute(
            sa.text('UPDATE objects SET sso_subject = :subject WHERE id = :object_id'),
            {'subject': account_subject, 'object_id': object_id},
        )
        connection.execute(
            sa.text(
                'INSERT INTO user_identity_objects (user_id, object_id) '
                'VALUES (:user_id, :object_id)'
            ),
            {'user_id': user_id, 'object_id': object_id},
        )
        assigned_users.add(user_id)
        assigned_objects.add(object_id)

    for user_id, candidate_object_ids in objects_by_user.items():
        if len(candidate_object_ids) != 1:
            continue
        object_id = next(iter(candidate_object_ids))
        if len(users_by_object[object_id]) != 1:
            continue
        assign_identity(user_id, object_id)

    # Older installations may have an ownership link but no retained invitation.
    # Use it only when exactly one owned object matches the account role by type code.
    owner_links = connection.execute(sa.text(
        """
        SELECT users.id, objects.id
        FROM users
        JOIN users_objects ON users_objects.user_id = users.id
        JOIN objects ON objects.id = users_objects.object_id
        JOIN object_types ON object_types.id = objects.type_id
        WHERE objects.deleted_at IS NULL
          AND object_types.code IN (users.role, users.role || 's')
        """
    )).all()
    owner_objects_by_user = defaultdict(set)
    owner_users_by_object = defaultdict(set)
    for user_id, object_id in owner_links:
        if user_id in assigned_users or object_id in assigned_objects:
            continue
        owner_objects_by_user[user_id].add(object_id)
        owner_users_by_object[object_id].add(user_id)

    for user_id, candidate_object_ids in owner_objects_by_user.items():
        if len(candidate_object_ids) != 1:
            continue
        object_id = next(iter(candidate_object_ids))
        if len(owner_users_by_object[object_id]) == 1:
            assign_identity(user_id, object_id)

    op.alter_column('objects', 'sso_subject', nullable=False)
    op.create_unique_constraint('uq_objects_sso_subject', 'objects', ['sso_subject'])
    op.drop_constraint('uq_users_sso_subject', 'users', type_='unique')
    op.drop_column('users', 'sso_subject')


def downgrade():
    op.add_column('users', sa.Column('sso_subject', sa.String(length=36), nullable=True))

    connection = op.get_bind()
    user_ids = connection.execute(sa.text('SELECT id FROM users')).scalars().all()
    for user_id in user_ids:
        object_subject = connection.execute(sa.text(
            """
            SELECT objects.sso_subject
            FROM user_identity_objects
            JOIN objects ON objects.id = user_identity_objects.object_id
            WHERE user_identity_objects.user_id = :user_id
            """
        ), {'user_id': user_id}).scalar_one_or_none()
        connection.execute(
            sa.text('UPDATE users SET sso_subject = :subject WHERE id = :user_id'),
            {'subject': object_subject or str(uuid.uuid4()), 'user_id': user_id},
        )

    op.alter_column('users', 'sso_subject', nullable=False)
    op.create_unique_constraint('uq_users_sso_subject', 'users', ['sso_subject'])
    op.drop_table('user_identity_objects')
    op.drop_constraint('uq_objects_sso_subject', 'objects', type_='unique')
    op.drop_column('objects', 'sso_subject')
