import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database.session import get_db
from app.modules.patient.model import Patient
from app.modules.pharmacogenomics.config import pgx_settings
from app.modules.pharmacogenomics.model import PGxReport
from app.modules.pharmacogenomics.schema import (
    GeneDrugPairInfo,
    PGxAnalyzeRequest,
    PGxPipelineResponse,
    PGxReportSummary,
)
from app.modules.pharmacogenomics.services.drug_matcher import GENE_DRUG_PAIRS
from app.modules.pharmacogenomics.services.pipeline import run_pgx_pipeline

router = APIRouter(
    prefix="/pharmacogenomics",
    tags=["Pharmacogenomics"],
)


@router.get("/ping")
def ping():
    return {
        "status": "active",
        "module": pgx_settings.MODULE_NAME,
        "version": pgx_settings.VERSION,
        "message": "GeneGuard Pharmacogenomics CDS Engine is operational 🧬💊"
    }


@router.get("/supported-drugs", response_model=List[GeneDrugPairInfo])
def get_supported_drugs(search: Optional[str] = Query(None, description="Optional search term")):
    """
    List all CPIC/PharmGKB supported medications, brand names, and associated gene-drug pairs.
    """
    if not search:
        return [GeneDrugPairInfo(**item) for item in GENE_DRUG_PAIRS]
        
    s = search.strip().lower()
    matched = []
    for item in GENE_DRUG_PAIRS:
        if (s in item["drug_name"].lower() or 
            any(s in b.lower() for b in item.get("brand_names", [])) or
            s in item["primary_gene"].lower() or
            s in item.get("therapeutic_area", "").lower()):
            matched.append(GeneDrugPairInfo(**item))
            
    return matched


@router.get("/supported-genes")
def get_supported_genes():
    """
    List all pharmacogenes covered by GeneGuard PGx with star-allele definition metadata.
    """
    allele_file = pgx_settings.DATA_DIR / "allele_definitions.json"
    if allele_file.exists():
        with open(allele_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "count": len(data),
                "genes": list(data.keys()),
                "details": data
            }
    return {"count": 0, "genes": []}


@router.post("/analyze", response_model=PGxPipelineResponse)
async def analyze_pharmacogenomics(
    request: PGxAnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Run full 12-stage Pharmacogenomics CDS pipeline for a patient and medication list.
    Automatically cross-references patient's WES report or uses provided variant list.
    """
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == request.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {request.patient_id} not found."
        )

    if not request.medications:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one medication must be provided in the medication list."
        )

    custom_variants = None
    if request.variants:
        custom_variants = [v.model_dump() for v in request.variants]

    try:
        results = await run_pgx_pipeline(
            patient_id=request.patient_id,
            medications=request.medications,
            custom_variants=custom_variants,
            db=db,
            use_latest_wes=request.use_latest_wes
        )
        return PGxPipelineResponse(**results)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pharmacogenomics analysis pipeline failed: {str(exc)}"
        ) from exc


@router.get("/patient/{patient_id}/reports", response_model=List[PGxReportSummary])
def get_patient_pgx_reports(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve all historical PGx reports generated for a patient.
    """
    reports = (
        db.query(PGxReport)
        .filter(PGxReport.patient_id == patient_id)
        .order_by(PGxReport.created_at.desc())
        .all()
    )
    
    return [
        PGxReportSummary(
            id=r.id,
            patient_id=r.patient_id,
            status=r.status,
            confidence_score=r.confidence_score,
            flagged_conflicts_count=r.flagged_conflicts_count,
            medications_evaluated=r.medications_evaluated,
            created_at=r.created_at
        )
        for r in reports
    ]


@router.get("/report/{report_id}")
def get_pgx_report_by_id(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve complete structured PGx recommendation package and evidence by report ID.
    """
    report = db.query(PGxReport).filter(PGxReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PGx report with ID {report_id} not found."
        )

    return {
        "report_id": report.id,
        "patient_id": report.patient_id,
        "status": report.status,
        "confidence_score": report.confidence_score,
        "flagged_conflicts_count": report.flagged_conflicts_count,
        "medications_evaluated": report.medications_evaluated,
        "recommendations": report.recommendations,
        "full_evidence_package": report.full_evidence_package,
        "created_at": report.created_at,
        "updated_at": report.updated_at
    }
