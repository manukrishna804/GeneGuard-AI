from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import jwt

from app.core.database.session import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
    oauth2_scheme
)
from app.modules.doctor.model import Doctor
from app.modules.doctor.schema import DoctorCreate, DoctorResponse, Token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

def get_current_doctor(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Doctor:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    doctor = db.query(Doctor).filter(Doctor.email == email).first()
    if doctor is None:
        raise credentials_exception
    return doctor

@router.post("/register", response_model=DoctorResponse)
def register(doctor_in: DoctorCreate, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.email == doctor_in.email).first()
    if doctor:
        raise HTTPException(
            status_code=400,
            detail="The doctor with this email already exists in the system.",
        )
    hashed_password = get_password_hash(doctor_in.password)
    new_doctor = Doctor(
        full_name=doctor_in.full_name,
        email=doctor_in.email,
        hashed_password=hashed_password,
        specialty=doctor_in.specialty,
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    doctor = db.query(Doctor).filter(Doctor.email == form_data.username).first()
    if not doctor or not verify_password(form_data.password, doctor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": doctor.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "doctor": doctor
    }

@router.get("/me", response_model=DoctorResponse)
def read_users_me(current_doctor: Doctor = Depends(get_current_doctor)):
    return current_doctor
