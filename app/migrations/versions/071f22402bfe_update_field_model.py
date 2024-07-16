"""update field model

Revision ID: 071f22402bfe
Revises: ac6edab0af44
Create Date: 2024-07-14 21:16:20.093517

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "071f22402bfe"
down_revision: Union[str, None] = "ac6edab0af44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("member", "company_id", existing_type=sa.INTEGER(), nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("member", "company_id", existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###
