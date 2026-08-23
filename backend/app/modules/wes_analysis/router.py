from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from sqlalchemy.orm import Session

from app.core.database.session import get_db
from app.modules.wes_analysis.schema import VariantInput, WESAnalysisResponse
from app.modules.wes_analysis.service import analyze_wes_report, analyze_single_variant
from app.modules.wes_analysis.model import WESReport

router = APIRouter(
    prefix="/wes",
    tags=["WES Analysis"]
)


@router.get("/health")
def health_check():
    """
    Check the health and status of the WES Analysis module.
    """
    return {
        "module": "wes_analysis",
        "status": "healthy"
    }


@router.post("/analyze", response_model=WESAnalysisResponse, response_model_exclude_none=True)
async def analyze_wes(
    file: UploadFile = File(...),
    patient_id: Optional[int] = Form(None),
    db: Optional[Session] = Depends(get_db),
):
    """
    Upload a WES report PDF, extract variant details, normalize them,
    and fetch comprehensive annotations from Ensembl, ClinVar, gnomAD, OMIM, and PubMed.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF files are supported."
        )

    try:
        file_bytes = await file.read()
        response = analyze_wes_report(file_bytes)

        # Save to database if DB session is active
        if db is not None:
            try:
                sample_id = None
                if response.reported_variant and response.reported_variant.gene:
                    sample_id = response.reported_variant.gene
                elif response.variants and response.variants[0].reported_variant:
                    sample_id = response.variants[0].reported_variant.gene

                report_entry = WESReport(
                    patient_id=patient_id,
                    report_name=file.filename,
                    file_path=f"uploads/{file.filename}",
                    sample_id=sample_id,
                    analysis_data=response.model_dump(exclude_none=True),
                )
                db.add(report_entry)
                db.commit()
            except Exception:
                if db:
                    db.rollback()

        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during WES analysis: {str(e)}"
        )


@router.post("/test-variant", response_model=WESAnalysisResponse, response_model_exclude_none=True)
def test_variant(variant: VariantInput):
    """
    Manually check a single variant's database connectivity/annotations
    without uploading a PDF.
    """
    try:
        return analyze_single_variant(variant)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during variant lookup: {str(e)}"
        )
