"""create database

Revision ID: 433c638ef15b
Revises: 
Create Date: 2024-04-25 22:37:39.233445

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '433c638ef15b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.Text(length=50), nullable=False),
    sa.Column('email', sa.Text(length=50), nullable=True),
    sa.Column('password', sa.Text(), nullable=False),
    sa.Column('token', sa.Text(), nullable=True),
    sa.Column('token_expiration', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('recipe',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('cook_time', sa.Integer(), nullable=True),
    sa.Column('prep_time', sa.Integer(), nullable=True),
    sa.Column('tips', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('recipe_id')
    )
    op.create_table('direction',
    sa.Column('direction_id', sa.Integer(), nullable=False),
    sa.Column('step_number', sa.Integer(), nullable=False),
    sa.Column('instruction', sa.Text(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.recipe_id'], ),
    sa.PrimaryKeyConstraint('direction_id')
    )
    op.create_table('favorite',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('is_favorite', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.recipe_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('user_id', 'recipe_id')
    )
    op.create_table('ingredient',
    sa.Column('ingredient_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=True),
    sa.Column('units', sa.Text(length=20), nullable=True),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.recipe_id'], ),
    sa.PrimaryKeyConstraint('ingredient_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ingredient')
    op.drop_table('favorite')
    op.drop_table('direction')
    op.drop_table('recipe')
    op.drop_table('user')
    # ### end Alembic commands ###
