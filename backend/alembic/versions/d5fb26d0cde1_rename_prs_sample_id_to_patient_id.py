"""rename prs sample id to patient id

Revision ID: d5fb26d0cde1
Revises: 2590b32ed42b
Create Date: 2026-09-06 20:21:38.384331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5fb26d0cde1'
down_revision: Union[str, Sequence[str], None] = '2590b32ed42b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    op.drop_constraint(
        "uq_prs_sample_disease",
        "prs_scores",
        type_="unique",
    )

    op.alter_column(
        "prs_scores",
        "sample_id",
        new_column_name="patient_id",
        existing_type=sa.String(length=100),
        existing_nullable=False,
    )

    op.create_unique_constraint(
        "uq_prs_patient_disease",
        "prs_scores",
        ["patient_id", "disease"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "uq_prs_patient_disease",
        "prs_scores",
        type_="unique",
    )

    op.alter_column(
        "prs_scores",
        "patient_id",
        new_column_name="sample_id",
        existing_type=sa.String(length=100),
        existing_nullable=False,
    )

    op.create_unique_constraint(
        "uq_prs_sample_disease",
        "prs_scores",
        ["sample_id", "disease"],
    )