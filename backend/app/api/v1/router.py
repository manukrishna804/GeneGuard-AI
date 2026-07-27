from fastapi import APIRouter

from app.api.v1.endpoints.patient import router as patient_router
from app.api.v1.endpoints.wes import router as wes_router
from app.api.v1.endpoints.family_history import router as family_history_router
from app.api.v1.endpoints.medication import router as medication_router

router = APIRouter()

router.include_router(patient_router)
router.include_router(wes_router)
router.include_router(family_history_router)
router.include_router(medication_router)


@router.get("/ping", tags=["Health"])
def ping():

    return {
        "message": "GeneGuard API is working successfully 🚀"
    }