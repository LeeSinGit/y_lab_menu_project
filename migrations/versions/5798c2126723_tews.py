"""tews

Revision ID: 5798c2126723
Revises:
Create Date: 2023-07-28 21:16:34.053277

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5798c2126723'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Menu',
                    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('submenus_count', sa.Integer(), nullable=True),
                    sa.Column('dishes_count', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('title')
                    )
    op.create_table('Submenu',
                    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('dishes_count', sa.Integer(), nullable=True),
                    sa.Column('menu_id', postgresql.UUID(), nullable=True),
                    sa.ForeignKeyConstraint(['menu_id'], ['Menu.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('title')
                    )
    op.create_table('Dish',
                    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('price', sa.String(), nullable=True),
                    sa.Column('submenu_id', postgresql.UUID(), nullable=True),
                    sa.ForeignKeyConstraint(['submenu_id'], ['Submenu.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('title')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Dish')
    op.drop_table('Submenu')
    op.drop_table('Menu')
    # ### end Alembic commands ###
