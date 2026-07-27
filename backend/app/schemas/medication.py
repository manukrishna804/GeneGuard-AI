from typing import Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class MedicationBase(BaseModel):
    patient_id: int
    drug_name: str
    gene: str
    genotype: Optional[str] = None
    metabolizer_status: Optional[str] = None
    cpic_recommendation: Optional[str] = None
    confidence_level: Optional[str] = None


# ---------------------------------------------------------------------------
# Create / Update
# ---------------------------------------------------------------------------

class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    """All fields optional for partial updates."""
    drug_name: Optional[str] = None
    gene: Optional[str] = None
    genotype: Optional[str] = None
    metabolizer_status: Optional[str] = None
    cpic_recommendation: Optional[str] = None
    confidence_level: Optional[str] = None


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class MedicationResponse(MedicationBase):
    id: int

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Lookup Request / Response (for medication_lookup service)
# ---------------------------------------------------------------------------

class MedicationLookupRequest(BaseModel):
    gene: str       # e.g. "CYP2D6"
    genotype: str   # e.g. "*1/*4"


class MedicationLookupResponse(BaseModel):
    gene: str
    genotype: str
    metabolizer_status: Optional[str] = None
    cpic_recommendation: Optional[str] = None
    confidence_level: Optional[str] = None
    source: str = "stub"   # "cpic_api" when live integration is added
