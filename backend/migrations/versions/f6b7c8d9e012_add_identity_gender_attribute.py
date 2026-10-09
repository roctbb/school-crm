"""Add an optional gender field to student and teacher profiles.

Revision ID: f6b7c8d9e012
Revises: ae91b38d720f
"""
from alembic import op
import sqlalchemy as sa

revision = 'f6b7c8d9e012'
down_revision = 'ae91b38d720f'
branch_labels = None
depends_on = None

GENDER_ATTRIBUTE = {
    'code': 'gender', 'name': 'Пол', 'type': 'select',
    'options': ['Мужской', 'Женский'],
    'required': False, 'display': True, 'show_off': False,
    'group': False, 'is_locked': False, 'is_private': False,
    'is_hidden': False, 'is_secret': False, 'keep_history': False,
    'description': '',
}


def _update_attributes(transform):
    table = sa.table('object_types', sa.column('id', sa.Integer),
                     sa.column('code', sa.String), sa.column('available_attributes', sa.JSON))
    connection = op.get_bind()
    for row in connection.execute(sa.select(table).where(
        table.c.code.in_(['student', 'students', 'teacher', 'teachers'])
    )).mappings():
        attributes = row['available_attributes'] or []
        updated = transform(attributes)
        if updated != attributes:
            connection.execute(table.update().where(table.c.id == row['id']).values(
                available_attributes=updated,
            ))


def upgrade():
    _update_attributes(lambda attributes: attributes if any(
        attribute.get('code') == 'gender' for attribute in attributes
    ) else [*attributes, GENDER_ATTRIBUTE])


def downgrade():
    # Preserve a field customized by an administrator and all entered values.
    _update_attributes(lambda attributes: [
        attribute for attribute in attributes if attribute != GENDER_ATTRIBUTE
    ])
