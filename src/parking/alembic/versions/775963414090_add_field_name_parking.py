"""add field name Parking

Revision ID: 775963414090
Revises: 6a771c40423b
Create Date: 2025-04-21 14:25:00.410858

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "775963414090"
down_revision: Union[str, None] = "6a771c40423b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("parkings", sa.Column("name", sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("parkings", "name")
    # ### end Alembic commands ###
