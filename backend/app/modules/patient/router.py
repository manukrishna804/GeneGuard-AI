from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database.session import get_db
from app.modules.patient.schema import PatientCreate, PatientResponse
from app.modules.patient.crud import create_patient, get_patients

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post("/", response_model=PatientResponse)
def create(patient: PatientCreate,
           db: Session = Depends(get_db)):

    return create_patient(db, patient)


@router.get("/", response_model=list[PatientResponse])
def read(db: Session = Depends(get_db)):

    return get_patients(db)