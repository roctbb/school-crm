"""empty message

Revision ID: c66783a9d6c0
Revises: b9c1de815bf7
Create Date: 2025-03-02 18:56:42.388226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c66783a9d6c0'
down_revision = 'b9c1de815bf7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('form_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('params', sa.JSON(), server_default=sa.text("'{}'::json"), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('forms', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'form_categories', ['category_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('forms', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('category_id')

    op.drop_table('form_categories')
    # ### end Alembic commands ###
