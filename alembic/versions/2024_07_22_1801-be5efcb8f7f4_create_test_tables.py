"""create test tables

Revision ID: be5efcb8f7f4
Revises: 0553b018a219
Create Date: 2024-07-22 18:01:16.045365

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "be5efcb8f7f4"
down_revision: Union[str, None] = "0553b018a219"
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