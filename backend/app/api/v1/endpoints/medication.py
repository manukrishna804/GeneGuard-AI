from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.medication import (
    MedicationCreate,
    MedicationLookupRequest,
    MedicationLookupResponse,
    MedicationResponse,
    MedicationUpdate,
)
from app.crud.medication import (
    create_medication,
    get_medication,
    get_medications_by_patient,
    update_medication,
    delete_medication,
)
from app.services.medication_lookup import lookup_recommendation

router = APIRouter(
    prefix="/medications",
    tags=["Medications"],
)


# ---------------------------------------------------------------------------
# CRUD Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=MedicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a medication/pharmacogenomics record for a patient",
)
def create(medication: MedicationCreate, db: Session = Depends(get_db)):
    return create_medication(db, medication)


@router.get(
    "/{medication_id}",
    response_model=MedicationResponse,
    summary="Get a single medication record by ID",
)
def get_by_id(medication_id: int, db: Session = Depends(get_db)):
    db_med = get_medication(db, medication_id)
    if not db_med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication record {medication_id} not found.",
        )
    return db_med


@router.get(
    "/patient/{patient_id}",
    response_model=List[MedicationResponse],
    summary="List all medication records for a patient",
)
def list_by_patient(patient_id: int, db: Session = Depends(get_db)):
    return get_medications_by_patient(db, patient_id)


@router.put(
    "/{medication_id}",
    response_model=MedicationResponse,
    summary="Update a medication record",
)
def update(
    medication_id: int,
    updates: MedicationUpdate,
    db: Session = Depends(get_db),
):
    db_med = update_medication(db, medication_id, updates)
    if not db_med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication record {medication_id} not found.",
        )
    return db_med


@router.delete(
    "/{medication_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a medication record",
)
def delete(medication_id: int, db: Session = Depends(get_db)):
    success = delete_medication(db, medication_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication record {medication_id} not found.",
        )


# ---------------------------------------------------------------------------
# Lookup Endpoint (calls medication_lookup service, no DB write)
# ---------------------------------------------------------------------------

@router.post(
    "/lookup",
    response_model=MedicationLookupResponse,
    summary="Look up CPIC pharmacogenomics recommendation for a gene + genotype",
)
def lookup(request: MedicationLookupRequest):
    """
    Returns a CPIC-guideline recommendation for the given gene/genotype combination.
    Currently uses a built-in stub knowledge base. When PharmGKB/CPIC API credentials
    are configured, set USE_API = True in services/medication_lookup.py.
    """
    result = lookup_recommendation(request.gene, request.genotype)
    return MedicationLookupResponse(**result)
