from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
import tempfile
import shutil
from app.core.database.session import SessionLocal
from .models import PRSScore
from .model_registry import PRS_MODELS

from .prs_pipeline import run_prs_pipeline

router = APIRouter(prefix="/prs", tags=["PRS"])


@router.post("/calculate")
async def calculate_prs(
    sample_id: str = Form(...),
    disease: str = Form("Type 2 diabetes"),
    vcf: UploadFile = File(...),
    vcf_index: UploadFile = File(...),
):
    if not vcf.filename:
        raise HTTPException(status_code=400, detail="VCF file is required")

    if not vcf_index.filename:
        raise HTTPException(status_code=400, detail="VCF index (.tbi) is required")

    if not vcf.filename.endswith(".vcf.gz"):
        raise HTTPException(
            status_code=400,
            detail="Compressed VCF (.vcf.gz) required",
        )

    if not vcf_index.filename.endswith(".tbi"):
        raise HTTPException(
            status_code=400,
            detail="VCF index (.tbi) required",
        )

    temp_dir = Path(tempfile.mkdtemp())

    vcf_path = temp_dir / "input.vcf.gz"
    tbi_path = temp_dir / "input.vcf.gz.tbi"

    try:
        with vcf_path.open("wb") as f:
            shutil.copyfileobj(vcf.file, f)

        with tbi_path.open("wb") as f:
            shutil.copyfileobj(vcf_index.file, f)
        
        if disease not in PRS_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"No PRS model configured for disease: {disease}",
            )
        
        result = run_prs_pipeline(
            vcf_path=str(vcf_path),
            pgs_path=str(PRS_MODELS[disease]["path"]),
            disease=disease,
            sample_id=sample_id,
            chromosomes=["10"] if PRS_MODELS[disease]["match_type"] == "position" else None,
            max_variants=5000,
            match_type=PRS_MODELS[disease]["match_type"],
        )
        db = SessionLocal()

        try:
            existing_score = (
                db.query(PRSScore)
                .filter(
                    PRSScore.sample_id == sample_id,
                    PRSScore.disease == disease,
                )
                .first()
            )

            if existing_score:
                existing_score.score_100 = result["score_100"]
            else:
                existing_score = PRSScore(
                    sample_id=sample_id,
                    disease=disease,
                    score_100=result["score_100"],
                )
                db.add(existing_score)

            db.commit()
            db.refresh(existing_score)

        finally:
            db.close()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)