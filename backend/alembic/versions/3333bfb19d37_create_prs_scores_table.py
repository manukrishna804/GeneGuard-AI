"""create prs scores table

Revision ID: 3333bfb19d37
Revises: 6512906493ab
Create Date: 2026-09-05 10:29:29.216699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3333bfb19d37'
down_revision: Union[str, Sequence[str], None] = '6512906493ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prs_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sample_id", sa.String(length=100), nullable=False),
        sa.Column("disease", sa.String(length=100), nullable=False),
        sa.Column("prs_score", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("prs_scores")