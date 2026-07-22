from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.patient import PatientCreate, PatientResponse
from app.crud.patient import create_patient, get_patients

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