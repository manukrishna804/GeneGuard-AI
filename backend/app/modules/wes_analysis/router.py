from fastapi import APIRouter, File, UploadFile, HTTPException
from app.modules.wes_analysis.schema import VariantInput, WESAnalysisResponse
from app.modules.wes_analysis.service import analyze_wes_report, analyze_single_variant

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


@router.post("/analyze", response_model=WESAnalysisResponse)
async def analyze_wes(file: UploadFile = File(...)):
    """
    Upload a WES report PDF, extract variant details, validate them,
    and fetch annotations from Ensembl and ClinVar.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF files are supported."
        )

    try:
        file_bytes = await file.read()
        return analyze_wes_report(file_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during WES analysis: {str(e)}"
        )


@router.post("/test-variant", response_model=WESAnalysisResponse)
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