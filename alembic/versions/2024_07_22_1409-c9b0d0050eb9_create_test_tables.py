"""create test tables

Revision ID: c9b0d0050eb9
Revises: eae7f7e02c98
Create Date: 2024-07-22 14:09:24.253676

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c9b0d0050eb9"
down_revision: Union[str, None] = "eae7f7e02c98"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
