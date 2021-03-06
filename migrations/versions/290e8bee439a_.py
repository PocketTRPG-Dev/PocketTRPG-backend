"""empty message

Revision ID: 290e8bee439a
Revises: 84ea2b3380ea
Create Date: 2020-02-09 16:59:30.155333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '290e8bee439a'
down_revision = '84ea2b3380ea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('map', sa.Column('size_hight', sa.Integer(), nullable=True))
    op.add_column('map', sa.Column('size_weight', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('map', 'size_weight')
    op.drop_column('map', 'size_hight')
    # ### end Alembic commands ###
