from fastapi import APIRouter

from .schema import (
    PharmacogenomicsRequest,
    PharmacogenomicsResponse,
)
from .services.pipeline import run_pharmacogenomics_pipeline


router = APIRouter(
    prefix="/pharmacogenomics",
    tags=["Pharmacogenomics"],
)


@router.get("/ping")
async def ping():
    return {
        "module": "pharmacogenomics",
        "status": "ok",
        "message": "Pharmacogenomics Module 5 is running",
    }



@router.post("/analyze", response_model=PharmacogenomicsResponse)
async def analyze_pharmacogenomics(
    request: PharmacogenomicsRequest,
):
    result = await run_pharmacogenomics_pipeline(
        variants=[
            variant.model_dump()
            for variant in request.variants
        ],
        medications=[
            medication.model_dump()
            for medication in request.medications
        ],
        clinical_indication=request.clinical_indication,
    )

    return PharmacogenomicsResponse(
        patient_id=request.patient_id,
        recommendations=result["recommendations"],
        flagged_conflicts=result["flagged_conflicts"],
        confidence=result["confidence"],
        specialist=(
            "Clinical Pharmacist"
            if result["flagged_conflicts"]
            else None
        ),
    )
