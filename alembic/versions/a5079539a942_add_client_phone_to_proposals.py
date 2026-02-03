"""add client_phone to proposals

Revision ID: a5079539a942
Revises: d3805892e443
Create Date: 2026-02-02 08:28:46.959878
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a5079539a942"
down_revision: Union[str, Sequence[str], None] = "d3805892e443"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "proposals",
        sa.Column("client_phone", sa.String(length=20), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("proposals", "client_phone")

