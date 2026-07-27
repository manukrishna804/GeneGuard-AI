from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship

from app.database.base import Base


class FamilyHistory(Base):
    """
    Represents a single family member node in a patient's family tree.

    Supports self-referencing via parent_id so a full pedigree tree can be built.
    Each patient_id groups a set of FamilyHistory rows into one family tree.
    """
    __tablename__ = "family_histories"

    id = Column(Integer, primary_key=True, index=True)

    # FK back to the patient this tree belongs to
    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )

    # Self-referencing: optional parent node within the same tree
    parent_id = Column(
        Integer,
        ForeignKey("family_histories.id"),
        nullable=True,
    )

    # Pedigree fields
    relationship_label = Column(String(100), nullable=True)   # e.g. "Father", "Maternal Grandmother"
    sex = Column(String(20), nullable=True)                    # "M", "F", "Unknown"
    health_status = Column(String(50), nullable=True)          # "Affected", "Unaffected", "Unknown"

    # Diagnosed conditions stored as a PostgreSQL native text array
    diagnosed_conditions = Column(ARRAY(String), nullable=True, default=list)

    # Per-condition carrier status: {"BRCA1": True, "CFTR": False}
    carrier_status = Column(JSONB, nullable=True)

    age = Column(Integer, nullable=True)

    # ORM relationships
    patient = relationship("Patient", back_populates="family_members")

    parent = relationship(
        "FamilyHistory",
        remote_side=[id],
        back_populates="children",
    )

    children = relationship(
        "FamilyHistory",
        back_populates="parent",
        cascade="all, delete-orphan",
    )