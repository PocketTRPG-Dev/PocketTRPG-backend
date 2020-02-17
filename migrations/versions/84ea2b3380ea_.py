"""empty message

Revision ID: 84ea2b3380ea
Revises: 745117847f98
Create Date: 2020-02-09 16:53:34.284999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84ea2b3380ea'
down_revision = '745117847f98'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('map',
    sa.Column('map_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.game_id'], ),
    sa.PrimaryKeyConstraint('map_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('map')
    # ### end Alembic commands ###
