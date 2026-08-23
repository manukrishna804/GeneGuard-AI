from sqlalchemy import Column, ForeignKey, Integer, String, JSON, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database.base import Base


class WESReport(Base):
    __tablename__ = "wes_reports"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=True
    )

    report_name = Column(String(255), nullable=True)

    file_path = Column(String(500), nullable=True)

    sample_id = Column(String(100), nullable=True)

    analysis_data = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    patient = relationship("Patient")