from sqlalchemy import Column, Integer, String, Float, UniqueConstraint

from app.core.database.base import Base


class PRSScore(Base):
    __tablename__ = "prs_scores"

    id = Column(Integer, primary_key=True)
    sample_id = Column(String(100), nullable=False)
    disease = Column(String(100), nullable=False)
    score_100 = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "sample_id",
            "disease",
            name="uq_prs_sample_disease",
        ),
    )