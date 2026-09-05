"""rename prs score to score 100

Revision ID: 33ddcda6c94f
Revises: 3333bfb19d37
Create Date: 2026-09-05 18:10:05.028960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '33ddcda6c94f'
down_revision: Union[str, Sequence[str], None] = '3333bfb19d37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "prs_scores",
        "prs_score",
        new_column_name="score_100",
    )


def downgrade() -> None:
    op.alter_column(
        "prs_scores",
        "score_100",
        new_column_name="prs_score",
    )
