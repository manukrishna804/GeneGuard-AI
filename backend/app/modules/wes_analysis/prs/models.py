from sqlalchemy import Column, Integer, String, Float, UniqueConstraint

from app.core.database.base import Base


class PRSScore(Base):
    __tablename__ = "prs_scores"

    id = Column(Integer, primary_key=True)

    patient_id = Column(
        String(100),
        nullable=False,
    )

    disease = Column(
        String(100),
        nullable=False,
    )

    raw_prs = Column(
        Float,
        nullable=False,
    )

    score_100 = Column(
        Float,
        nullable=False,
    )

    score_100_status = Column(
        String(50),
        nullable=False,
    )

    score_100_reference = Column(
        String(50),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "patient_id",
            "disease",
            name="uq_prs_patient_disease",
        ),
    )