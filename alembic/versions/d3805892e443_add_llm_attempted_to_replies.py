"""add llm_attempted to replies

Revision ID: d3805892e443
Revises: 61da5dc5420d
Create Date: 2026-01-28 11:58:38.417798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3805892e443'
down_revision: Union[str, Sequence[str], None] = '61da5dc5420d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "replies",
        sa.Column("llm_attempted", sa.Boolean(), server_default="0")
    )


def downgrade() -> None:
    op.drop_column("replies", "llm_attempted")



