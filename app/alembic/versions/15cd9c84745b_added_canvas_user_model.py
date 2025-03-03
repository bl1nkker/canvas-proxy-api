"""added canvas user model

Revision ID: 15cd9c84745b
Revises: 3139ddd9ed90
Create Date: 2025-03-03 10:18:45.255827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15cd9c84745b'
down_revision: Union[str, None] = '3139ddd9ed90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('canvas_users',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('canvas_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('version_id', sa.Integer(), nullable=False),
    sa.Column('created_date', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_date', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('web_id', sa.String(length=32), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['app.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('canvas_id'),
    sa.UniqueConstraint('username'),
    sa.UniqueConstraint('web_id'),
    schema='app'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('canvas_users', schema='app')
    # ### end Alembic commands ###
