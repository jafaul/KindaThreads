"""create test tables

Revision ID: 3f3f7203c147
Revises: 296a1bc9e8bb
Create Date: 2024-07-22 15:36:58.632707

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3f3f7203c147"
down_revision: Union[str, None] = "296a1bc9e8bb"
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