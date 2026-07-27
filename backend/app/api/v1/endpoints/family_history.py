from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.family_history import (
    FamilyMemberCreate,
    FamilyMemberResponse,
    FamilyMemberUpdate,
    FamilyMemberWithChildren,
    FamilyTreeResponse,
)
from app.crud.family_history import (
    create_family_member,
    get_family_member,
    get_family_members_by_patient,
    get_root_members_by_patient,
    update_family_member,
    delete_family_member,
)
from app.services.genetics_engine import (
    CarrierStatus,
    InheritanceMode,
    detect_inheritance_pattern,
    family_history_to_pedigree,
    punnett_square,
)

router = APIRouter(
    prefix="/family-members",
    tags=["Family History"],
)


# ---------------------------------------------------------------------------
# Helper — build nested tree from flat list
# ---------------------------------------------------------------------------

def _build_tree(
    members: List, id_to_node: Dict[int, FamilyMemberWithChildren]
) -> List[FamilyMemberWithChildren]:
    """Recursively attach children to their parent node and return root nodes."""
    roots: List[FamilyMemberWithChildren] = []
    for m in members:
        node = id_to_node[m.id]
        if m.parent_id is None or m.parent_id not in id_to_node:
            roots.append(node)
        else:
            id_to_node[m.parent_id].children.append(node)
    return roots


# ---------------------------------------------------------------------------
# CRUD Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=FamilyMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a family member to a patient's pedigree",
)
def create_member(
    member: FamilyMemberCreate,
    db: Session = Depends(get_db),
):
    return create_family_member(db, member)


@router.get(
    "/{member_id}",
    response_model=FamilyMemberResponse,
    summary="Get a single family member by ID",
)
def get_member(member_id: int, db: Session = Depends(get_db)):
    db_member = get_family_member(db, member_id)
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family member {member_id} not found.",
        )
    return db_member


@router.get(
    "/patient/{patient_id}",
    response_model=List[FamilyMemberResponse],
    summary="List all family members for a patient (flat list)",
)
def list_members(patient_id: int, db: Session = Depends(get_db)):
    return get_family_members_by_patient(db, patient_id)


@router.put(
    "/{member_id}",
    response_model=FamilyMemberResponse,
    summary="Update a family member",
)
def update_member(
    member_id: int,
    updates: FamilyMemberUpdate,
    db: Session = Depends(get_db),
):
    db_member = update_family_member(db, member_id, updates)
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family member {member_id} not found.",
        )
    return db_member


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a family member (cascades to children)",
)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    success = delete_family_member(db, member_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family member {member_id} not found.",
        )


# ---------------------------------------------------------------------------
# Tree Endpoint
# ---------------------------------------------------------------------------

@router.get(
    "/patient/{patient_id}/tree",
    response_model=FamilyTreeResponse,
    summary="Get the full family tree for a patient (nested structure)",
)
def get_family_tree(patient_id: int, db: Session = Depends(get_db)):
    members = get_family_members_by_patient(db, patient_id)
    id_to_node: Dict[int, FamilyMemberWithChildren] = {
        m.id: FamilyMemberWithChildren.model_validate(m) for m in members
    }
    roots = _build_tree(members, id_to_node)
    return FamilyTreeResponse(patient_id=patient_id, roots=roots)


# ---------------------------------------------------------------------------
# Genetics Analysis Endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/patient/{patient_id}/analyze",
    summary="Run inheritance pattern analysis on a patient's family tree",
)
def analyze_family_tree(patient_id: int, db: Session = Depends(get_db)):
    """
    Returns:
    - The detected inheritance pattern and confidence
    - Punnett square probabilities if exactly two parents with known carrier status exist
    """
    members = get_family_members_by_patient(db, patient_id)
    if not members:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No family members found for patient {patient_id}.",
        )

    pedigree = family_history_to_pedigree(members)
    pattern_result = detect_inheritance_pattern(pedigree)

    # Punnett square: compute if we can find two root nodes (likely parents)
    roots = [m for m in pedigree if m.parent_id is None]
    punnett_result: Optional[Dict] = None

    if len(roots) == 2:
        inferred_mode = InheritanceMode(pattern_result["pattern"]) \
            if pattern_result["pattern"] in [m.value for m in InheritanceMode] \
            else InheritanceMode.AUTOSOMAL_RECESSIVE

        def _infer_status(node) -> CarrierStatus:
            if node.health_status == "Affected":
                return CarrierStatus.AFFECTED
            # Check carrier_status dict for any True entry
            if node.carrier_status and any(node.carrier_status.values()):
                return CarrierStatus.CARRIER
            if node.health_status == "Unaffected":
                return CarrierStatus.UNAFFECTED
            return CarrierStatus.UNKNOWN

        p1_status = _infer_status(roots[0])
        p2_status = _infer_status(roots[1])
        punnett_result = punnett_square(p1_status, p2_status, inferred_mode)
        punnett_result["parent1"] = roots[0].relationship_label or f"Member {roots[0].member_id}"
        punnett_result["parent2"] = roots[1].relationship_label or f"Member {roots[1].member_id}"
        punnett_result["inheritance_mode"] = inferred_mode.value

    return {
        "patient_id": patient_id,
        "total_members": len(members),
        "inheritance_analysis": pattern_result,
        "punnett_square": punnett_result,
    }
