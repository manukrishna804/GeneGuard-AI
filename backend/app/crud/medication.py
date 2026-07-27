from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.medication import Medication
from app.schemas.medication import MedicationCreate, MedicationUpdate


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_medication(db: Session, medication: MedicationCreate) -> Medication:
    db_med = Medication(
        patient_id=medication.patient_id,
        drug_name=medication.drug_name,
        gene=medication.gene,
        genotype=medication.genotype,
        metabolizer_status=medication.metabolizer_status,
        cpic_recommendation=medication.cpic_recommendation,
        confidence_level=medication.confidence_level,
    )
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return db_med


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def get_medication(db: Session, medication_id: int) -> Optional[Medication]:
    return db.query(Medication).filter(Medication.id == medication_id).first()


def get_medications_by_patient(
    db: Session, patient_id: int
) -> List[Medication]:
    return (
        db.query(Medication)
        .filter(Medication.patient_id == patient_id)
        .order_by(Medication.id)
        .all()
    )


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_medication(
    db: Session, medication_id: int, updates: MedicationUpdate
) -> Optional[Medication]:
    db_med = get_medication(db, medication_id)
    if not db_med:
        return None

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_med, field, value)

    db.commit()
    db.refresh(db_med)
    return db_med


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_medication(db: Session, medication_id: int) -> bool:
    db_med = get_medication(db, medication_id)
    if not db_med:
        return False
    db.delete(db_med)
    db.commit()
    return True
