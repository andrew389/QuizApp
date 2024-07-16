"""update model

Revision ID: ac6edab0af44
Revises: cd4c2418abdd
Create Date: 2024-07-14 18:31:18.325729

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ac6edab0af44"
down_revision: Union[str, None] = "cd4c2418abdd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("company", sa.Column("is_visible", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("company", "is_visible")
    # ### end Alembic commands ###
