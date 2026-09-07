from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Float
from sqlalchemy.orm import relationship

from app.core.database.base import Base


class PGxReport(Base):
    __tablename__ = "pgx_reports"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    status = Column(
        String(50),
        nullable=False,
        default="completed"
    )

    confidence_score = Column(
        Float,
        nullable=False,
        default=95.0
    )

    flagged_conflicts_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    medications_evaluated = Column(
        JSON,
        nullable=True
    )

    recommendations = Column(
        JSON,
        nullable=True
    )

    full_evidence_package = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    patient = relationship("Patient")
