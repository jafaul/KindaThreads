"""create test tables

Revision ID: 7f7a7aa901ee
Revises: a6de7cb5aea6
Create Date: 2024-07-22 16:48:46.456641

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f7a7aa901ee"
down_revision: Union[str, None] = "a6de7cb5aea6"
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