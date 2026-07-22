from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class AIReport(Base):
    __tablename__ = "ai_reports"

    id = Column(Integer, primary_key=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    report = Column(Text)

    patient = relationship("Patient")