from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class Lifestyle(Base):
    __tablename__ = "lifestyles"

    id = Column(Integer, primary_key=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    lifestyle_data = Column(Text)

    patient = relationship("Patient")