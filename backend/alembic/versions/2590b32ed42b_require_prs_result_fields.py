"""require prs result fields

Revision ID: 2590b32ed42b
Revises: 61c86fe1defc
Create Date: 2026-09-06 10:39:39.920597

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2590b32ed42b'
down_revision: Union[str, Sequence[str], None] = '61c86fe1defc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "prs_scores",
        "raw_prs",
        existing_type=sa.Float(),
        nullable=False,
    )

    op.alter_column(
        "prs_scores",
        "score_100_status",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    op.alter_column(
        "prs_scores",
        "score_100_reference",
        existing_type=sa.String(length=50),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "prs_scores",
        "score_100_reference",
        existing_type=sa.String(length=50),
        nullable=True,
    )

    op.alter_column(
        "prs_scores",
        "score_100_status",
        existing_type=sa.String(length=50),
        nullable=True,
    )

    op.alter_column(
        "prs_scores",
        "raw_prs",
        existing_type=sa.Float(),
        nullable=True,
    )