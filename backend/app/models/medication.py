from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class Medication(Base):
    """
    Pharmacogenomics medication record for a patient.

    Captures gene-drug interaction data following CPIC (Clinical Pharmacogenomics
    Implementation Consortium) guidelines.
    """
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )

    drug_name = Column(String(200), nullable=False)

    gene = Column(String(50), nullable=False)          # e.g. "CYP2D6", "CYP2C19"

    genotype = Column(String(100), nullable=True)      # e.g. "*1/*4", "*2/*2"

    metabolizer_status = Column(
        String(50), nullable=True
    )                                                  # "poor", "intermediate", "normal", "rapid", "ultrarapid"

    cpic_recommendation = Column(Text, nullable=True)  # Full recommendation text

    confidence_level = Column(
        String(20), nullable=True
    )                                                  # "strong", "moderate", "weak"

    # ORM relationship
    patient = relationship("Patient", back_populates="medications")
