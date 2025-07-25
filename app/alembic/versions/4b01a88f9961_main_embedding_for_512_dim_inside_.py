"""main embedding for 512 dim inside student vector

Revision ID: 4b01a88f9961
Revises: eee34468778d
Create Date: 2025-04-28 13:22:08.657131

"""

from typing import Sequence, Union
import pgvector
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4b01a88f9961"
down_revision: Union[str, None] = "eee34468778d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("TRUNCATE TABLE app.student_vectors RESTART IDENTITY CASCADE;")
    op.alter_column(
        "student_vectors",
        "embedding",
        existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=192),
        type_=pgvector.sqlalchemy.vector.VECTOR(dim=512),
        existing_nullable=False,
        schema="app",
    )
    op.drop_column("student_vectors", "embedding_512", schema="app")
    op.drop_column("student_vectors", "embedding_4096", schema="app")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "student_vectors",
        sa.Column(
            "embedding_4096",
            pgvector.sqlalchemy.vector.VECTOR(dim=4096),
            autoincrement=False,
            nullable=True,
        ),
        schema="app",
    )
    op.add_column(
        "student_vectors",
        sa.Column(
            "embedding_512",
            pgvector.sqlalchemy.vector.VECTOR(dim=512),
            autoincrement=False,
            nullable=True,
        ),
        schema="app",
    )
    op.alter_column(
        "student_vectors",
        "embedding",
        existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=512),
        type_=pgvector.sqlalchemy.vector.VECTOR(dim=192),
        existing_nullable=False,
        schema="app",
    )
    # ### end Alembic commands ###
