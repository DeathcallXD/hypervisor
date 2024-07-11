"""adding nullable to org_id

Revision ID: 2
Revises: 1
Create Date: 2024-07-10 19:30:35.816028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2'
down_revision: Union[str, None] = '1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'organisation_id',
               existing_type=sa.VARCHAR(length=19),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'organisation_id',
               existing_type=sa.VARCHAR(length=19),
               nullable=False)
    # ### end Alembic commands ###
