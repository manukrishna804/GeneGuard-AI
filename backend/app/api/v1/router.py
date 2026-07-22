from fastapi import APIRouter

from app.api.v1.endpoints.patient import router as patient_router

router = APIRouter()

router.include_router(patient_router)


@router.get("/ping", tags=["Health"])
def ping():

    return {
        "message": "GeneGuard API is working successfully 🚀"
    }