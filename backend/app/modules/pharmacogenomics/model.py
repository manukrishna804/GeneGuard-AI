from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base


class PharmacogenomicsReport(Base):
    """
    Stores the final Module 5 pharmacogenomics analysis.

    Module 5 generates a structured PGx recommendation package
    which can later be consumed by Module 6.
    """

    __tablename__ = "pharmacogenomics_reports"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    patient_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    recommendations: Mapped[list[Any]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    flagged_conflicts: Mapped[list[Any]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    confidence: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    specialist: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )