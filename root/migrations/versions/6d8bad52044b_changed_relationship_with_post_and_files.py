"""Changed relationship with post and files

Revision ID: 6d8bad52044b
Revises: 3464a2bb50bd
Create Date: 2023-06-10 16:27:52.450714

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d8bad52044b'
down_revision = '3464a2bb50bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('files', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file_post_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'posts', ['file_post_id'], ['post_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('files', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('file_post_id')

    # ### end Alembic commands ###
