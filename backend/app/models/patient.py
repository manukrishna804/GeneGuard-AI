from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100), nullable=False)

    age = Column(Integer)

    gender = Column(String(20))

    email = Column(String(100), unique=True, nullable=True)

    # Relationships
    family_members = relationship(
        "FamilyHistory",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    medications = relationship(
        "Medication",
        back_populates="patient",
        cascade="all, delete-orphan",
    )