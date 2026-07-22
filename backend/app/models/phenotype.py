from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class Phenotype(Base):
    __tablename__ = "phenotypes"

    id = Column(Integer, primary_key=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    symptoms = Column(Text)

    patient = relationship("Patient")