from pydantic import BaseModel, EmailStr
from typing import Optional

class DoctorCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    specialty: Optional[str] = None

class DoctorResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    specialty: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    doctor: DoctorResponse
