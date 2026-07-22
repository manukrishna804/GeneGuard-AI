from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class WESReport(Base):
    __tablename__ = "wes_reports"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    report_name = Column(String(255))

    file_path = Column(String(500))

    patient = relationship("Patient")