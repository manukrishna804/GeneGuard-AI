from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.core.database.base import Base


class WESReport(Base):
    __tablename__ = "wes_reports"

    id = Column(Integer, primary_key=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
    )

    report_name = Column(String(255))

    status = Column(
        String(50),
        nullable=False,
        default="pending",
    )

    analysis_result = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    patient = relationship("Patient")