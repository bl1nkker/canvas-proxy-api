"""added failed and error_json to attendances

Revision ID: 40e6fb4b7f51
Revises: a14ecb624c99
Create Date: 2025-03-31 12:33:01.924604

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "40e6fb4b7f51"
down_revision: Union[str, None] = "a14ecb624c99"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "attendances", sa.Column("failed", sa.Boolean(), nullable=True), schema="app"
    )
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM app.attendances"))
    for row in result:
        conn.execute(
            sa.text("UPDATE app.attendances SET failed = :failed WHERE id = :id"),
            {"failed": False, "id": row[0]},
        )
    op.alter_column("attendances", "failed", nullable=False, schema="app")
    op.add_column(
        "attendances",
        sa.Column("error_json", sa.JSON(none_as_null=True), nullable=True),
        schema="app",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("attendances", "error_json", schema="app")
    op.drop_column("attendances", "failed", schema="app")
    # ### end Alembic commands ###
