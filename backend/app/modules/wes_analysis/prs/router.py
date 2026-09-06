from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
import tempfile
import shutil

from app.core.database.session import SessionLocal

from .models import PRSScore
from .model_registry import PRS_MODELS
from .prs_pipeline import run_prs_pipeline


router = APIRouter(
    prefix="/prs",
    tags=["PRS"],
)


@router.post("/calculate")
async def calculate_prs(
    sample_id: str = Form(...),
    vcf: UploadFile = File(...),
    vcf_index: UploadFile = File(...),
):
    """
    Calculate PRS for all configured diseases from one VCF.
    """

    # --------------------------------------------------
    # Validate uploads
    # --------------------------------------------------

    if not vcf.filename:
        raise HTTPException(
            status_code=400,
            detail="VCF file is required",
        )

    if not vcf_index.filename:
        raise HTTPException(
            status_code=400,
            detail="VCF index (.tbi) is required",
        )

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

    if not sample_id.strip():
        raise HTTPException(
            status_code=400,
            detail="sample_id is required",
        )
    sample_id = sample_id.strip()

    temp_dir = Path(
        tempfile.mkdtemp()
    )

    vcf_path = (
        temp_dir / "input.vcf.gz"
    )

    tbi_path = (
        temp_dir / "input.vcf.gz.tbi"
    )

    try:
        # --------------------------------------------------
        # Save uploaded VCF
        # --------------------------------------------------

        with vcf_path.open("wb") as file:
            shutil.copyfileobj(
                vcf.file,
                file,
            )

        # --------------------------------------------------
        # Save uploaded VCF index
        # --------------------------------------------------

        with tbi_path.open("wb") as file:
            shutil.copyfileobj(
                vcf_index.file,
                file,
            )

        # --------------------------------------------------
        # Run all configured PRS models
        # --------------------------------------------------

        results = []

        for disease, model in PRS_MODELS.items():

            try:
                result = run_prs_pipeline(
                    vcf_path=str(
                        vcf_path
                    ),
                    pgs_path=str(
                        model["path"]
                    ),
                    disease=disease,
                    sample_id=sample_id,
                    max_variants=model.get(
                        "development_limit"
                    ),
                    match_type=model[
                        "match_type"
                    ],
                )

                results.append(result)

            except Exception as exc:
                results.append(
                    {
                        "disease": disease,
                        "sample_id": sample_id,
                        "pgs_id": model["pgs_id"],
                        "status": "ERROR",
                        "error": str(exc),
                    }
                )

        # --------------------------------------------------
        # Save results
        # --------------------------------------------------

        db = SessionLocal()

        try:

            for result in results:

                if result.get("status") == "ERROR":
                    continue

                existing_score = (
                    db.query(PRSScore)
                    .filter(
                        PRSScore.sample_id
                        == sample_id,
                        PRSScore.disease
                        == result["disease"],
                    )
                    .first()
                )

                if existing_score:
                    existing_score.raw_prs = result["prs"]
                    existing_score.score_100 = result["score_100"]
                    existing_score.score_100_status = result["score_100_status"]
                    existing_score.score_100_reference = result["score_100_reference"]
                else:

                    db.add(
                        PRSScore(
                            sample_id=sample_id,
                            disease=result["disease"],
                            raw_prs=result["prs"],
                            score_100=result["score_100"],
                            score_100_status=result["score_100_status"],
                            score_100_reference=result["score_100_reference"],
                        )
                    )

            db.commit()

        finally:
            db.close()

        # --------------------------------------------------
        # Return all results
        # --------------------------------------------------

        return {
            "sample_id": sample_id,
            "diseases_processed": len(results),
            "results": results,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:
        shutil.rmtree(
            temp_dir,
            ignore_errors=True,
        )