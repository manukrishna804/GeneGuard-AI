from pydantic import BaseModel, EmailStr
from typing import Optional


class PatientBase(BaseModel):
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    email: Optional[EmailStr] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int

    model_config = {
        "from_attributes": True
    }