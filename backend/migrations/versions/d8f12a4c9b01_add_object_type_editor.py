"""add object type editor support

Revision ID: d8f12a4c9b01
Revises: 9c8d9a8e1304
Create Date: 2026-08-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd8f12a4c9b01'
down_revision = '9c8d9a8e1304'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint('uq_object_types_code', 'object_types', ['code'])

    op.create_table(
        'object_type_revisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('object_type_id', sa.Integer(), nullable=False),
        sa.Column('editor_id', sa.Integer(), nullable=True),
        sa.Column('snapshot', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['editor_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['object_type_id'], ['object_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_object_type_revisions_object_type_id',
        'object_type_revisions',
        ['object_type_id'],
        unique=False,
    )

    # Участники получают историю фотографий в JSON без отдельной таблицы.
    op.execute(
        """
        UPDATE object_types
        SET available_attributes = (
            SELECT json_agg(
                CASE
                    WHEN attribute->>'code' = 'photo'
                    THEN attribute::jsonb || '{"keep_history": true}'::jsonb
                    ELSE attribute::jsonb
                END
                ORDER BY position
            )
            FROM json_array_elements(available_attributes) WITH ORDINALITY AS attrs(attribute, position)
        )
        WHERE code IN ('students', 'teachers')
        """
    )


def downgrade():
    op.execute(
        """
        UPDATE object_types
        SET available_attributes = (
            SELECT json_agg((attribute::jsonb - 'keep_history') ORDER BY position)
            FROM json_array_elements(available_attributes) WITH ORDINALITY AS attrs(attribute, position)
        )
        WHERE code IN ('students', 'teachers')
        """
    )
    op.drop_index('ix_object_type_revisions_object_type_id', table_name='object_type_revisions')
    op.drop_table('object_type_revisions')
    op.drop_constraint('uq_object_types_code', 'object_types', type_='unique')
