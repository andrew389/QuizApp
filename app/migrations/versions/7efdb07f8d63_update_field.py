"""update field

Revision ID: 7efdb07f8d63
Revises: 071f22402bfe
Create Date: 2024-07-15 11:47:54.445466

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7efdb07f8d63"
down_revision: Union[str, None] = "071f22402bfe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("password", sa.String(), nullable=True))
    op.drop_column("user", "hashed_password")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user",
        sa.Column("hashed_password", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_column("user", "password")
    # ### end Alembic commands ###
