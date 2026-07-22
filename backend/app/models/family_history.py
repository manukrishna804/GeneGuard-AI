from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class FamilyHistory(Base):
    __tablename__ = "family_histories"

    id = Column(Integer, primary_key=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    history = Column(Text)

    patient = relationship("Patient")