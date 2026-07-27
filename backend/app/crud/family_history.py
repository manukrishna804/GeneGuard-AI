from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.family_history import FamilyHistory
from app.schemas.family_history import FamilyMemberCreate, FamilyMemberUpdate


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_family_member(db: Session, member: FamilyMemberCreate) -> FamilyHistory:
    db_member = FamilyHistory(
        patient_id=member.patient_id,
        parent_id=member.parent_id,
        relationship_label=member.relationship_label,
        sex=member.sex,
        health_status=member.health_status,
        diagnosed_conditions=member.diagnosed_conditions or [],
        carrier_status=member.carrier_status,
        age=member.age,
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def get_family_member(db: Session, member_id: int) -> Optional[FamilyHistory]:
    return db.query(FamilyHistory).filter(FamilyHistory.id == member_id).first()


def get_family_members_by_patient(
    db: Session, patient_id: int
) -> List[FamilyHistory]:
    return (
        db.query(FamilyHistory)
        .filter(FamilyHistory.patient_id == patient_id)
        .order_by(FamilyHistory.id)
        .all()
    )


def get_root_members_by_patient(
    db: Session, patient_id: int
) -> List[FamilyHistory]:
    """Returns only top-level nodes (parent_id IS NULL) for tree rendering."""
    return (
        db.query(FamilyHistory)
        .filter(
            FamilyHistory.patient_id == patient_id,
            FamilyHistory.parent_id == None,  # noqa: E711
        )
        .order_by(FamilyHistory.id)
        .all()
    )


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_family_member(
    db: Session, member_id: int, updates: FamilyMemberUpdate
) -> Optional[FamilyHistory]:
    db_member = get_family_member(db, member_id)
    if not db_member:
        return None

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_member, field, value)

    db.commit()
    db.refresh(db_member)
    return db_member


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_family_member(db: Session, member_id: int) -> bool:
    db_member = get_family_member(db, member_id)
    if not db_member:
        return False
    db.delete(db_member)
    db.commit()
    return True
