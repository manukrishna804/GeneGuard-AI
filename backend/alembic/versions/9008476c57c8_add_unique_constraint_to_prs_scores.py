"""add unique constraint to prs scores

Revision ID: 9008476c57c8
Revises: 33ddcda6c94f
Create Date: 2026-09-05 18:43:40.824519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9008476c57c8'
down_revision: Union[str, Sequence[str], None] = '33ddcda6c94f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_prs_sample_disease",
        "prs_scores",
        ["sample_id", "disease"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_prs_sample_disease",
        "prs_scores",
        type_="unique",
    )