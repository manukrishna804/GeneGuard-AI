from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Base — shared fields
# ---------------------------------------------------------------------------

class FamilyMemberBase(BaseModel):
    patient_id: int
    parent_id: Optional[int] = None
    relationship_label: Optional[str] = None
    sex: Optional[str] = None                        # "M", "F", "Unknown"
    health_status: Optional[str] = None              # "Affected", "Unaffected", "Unknown"
    diagnosed_conditions: Optional[List[str]] = None # ["BRCA1 mutation", "CFTR carrier"]
    carrier_status: Optional[Dict[str, bool]] = None # {"CFTR": True, "BRCA1": False}
    age: Optional[int] = None


# ---------------------------------------------------------------------------
# Create / Update
# ---------------------------------------------------------------------------

class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberUpdate(BaseModel):
    """All fields optional for partial updates."""
    parent_id: Optional[int] = None
    relationship_label: Optional[str] = None
    sex: Optional[str] = None
    health_status: Optional[str] = None
    diagnosed_conditions: Optional[List[str]] = None
    carrier_status: Optional[Dict[str, bool]] = None
    age: Optional[int] = None


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class FamilyMemberResponse(FamilyMemberBase):
    id: int

    model_config = {"from_attributes": True}


class FamilyMemberWithChildren(FamilyMemberResponse):
    """Recursive model for tree rendering."""
    children: List[FamilyMemberWithChildren] = []


class FamilyTreeResponse(BaseModel):
    patient_id: int
    roots: List[FamilyMemberWithChildren]  # top-level nodes (parent_id is None)
