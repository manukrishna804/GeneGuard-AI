"""add raw prs to prs scores

Revision ID: 61c86fe1defc
Revises: 9008476c57c8
Create Date: 2026-09-06 10:09:21.967968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61c86fe1defc'
down_revision: Union[str, Sequence[str], None] = '9008476c57c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "prs_scores",
        sa.Column("raw_prs", sa.Float(), nullable=True),
    )
    op.add_column(
        "prs_scores",
        sa.Column("score_100_status", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "prs_scores",
        sa.Column("score_100_reference", sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("prs_scores", "raw_prs")