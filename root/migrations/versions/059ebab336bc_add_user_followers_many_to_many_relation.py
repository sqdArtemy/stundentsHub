"""Add user_followers many-to-many relation.

Revision ID: 059ebab336bc
Revises: a0a8974312e5
Create Date: 2023-06-08 13:05:16.322425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '059ebab336bc'
down_revision = 'a0a8974312e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_follower',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['follower_id'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_follower')
    # ### end Alembic commands ###