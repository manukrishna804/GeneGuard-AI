from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
import tempfile
import shutil
import subprocess

from app.core.database.session import SessionLocal

from .models import PRSScore
from .model_registry import PRS_MODELS
from .prs_pipeline import run_prs_pipeline
from .vcf_parser import _windows_to_wsl_path


router = APIRouter(
    prefix="/prs",
    tags=["PRS"],
)


def _get_vcf_sample_id(vcf_path: Path) -> str:
    """
    Read the first sample ID from the VCF header.

    The VCF sample ID is used internally by bcftools.
    It is NOT used as the application's patient_id.
    """

    try:
        result = subprocess.run(
            [
                "wsl",
                "bcftools",
                "query",
                "-l",
                _windows_to_wsl_path(vcf_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="WSL or bcftools is not available.",
        ) from exc

    except subprocess.CalledProcessError as exc:
        error_message = (
            exc.stderr.strip()
            or exc.stdout.strip()
            or "Unable to read VCF sample information."
        )

        raise HTTPException(
            status_code=400,
            detail=error_message,
        ) from exc

    sample_ids = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]

    if not sample_ids:
        raise HTTPException(
            status_code=400,
            detail="No sample ID was found in the uploaded VCF.",
        )

    if len(sample_ids) > 1:
        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded VCF contains multiple samples. "
                "Please upload a VCF containing one patient sample."
            ),
        )

    return sample_ids[0]


@router.post("/calculate")
async def calculate_prs(
    patient_id: str = Form(...),
    vcf: UploadFile = File(...),
    vcf_index: UploadFile | None = File(None),
):
    """
    Calculate PRS for all configured diseases from one patient VCF.

    patient_id:
        GeneGuard's application-level unique patient ID.

    vcf:
        Patient genotype VCF (.vcf.gz).

    vcf_index:
        Optional VCF index (.tbi).
        If omitted, the backend creates it automatically.
    """

    # --------------------------------------------------
    # Validate VCF
    # --------------------------------------------------

    if not vcf.filename:
        raise HTTPException(
            status_code=400,
            detail="VCF file is required.",
        )

    if not vcf.filename.lower().endswith(".vcf.gz"):
        raise HTTPException(
            status_code=400,
            detail="Compressed VCF (.vcf.gz) required.",
        )

    # --------------------------------------------------
    # Validate optional VCF index
    # --------------------------------------------------

    if vcf_index is not None:

        if (
            not vcf_index.filename
            or not vcf_index.filename.lower().endswith(".tbi")
        ):
            raise HTTPException(
                status_code=400,
                detail="VCF index must be a .tbi file.",
            )

    # --------------------------------------------------
    # Validate GeneGuard patient ID
    # --------------------------------------------------

    if not patient_id.strip():
        raise HTTPException(
            status_code=400,
            detail="patient_id is required.",
        )

    patient_id = patient_id.strip()

    # --------------------------------------------------
    # Temporary working directory
    # --------------------------------------------------

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
        # Save provided index OR create one
        # --------------------------------------------------

        if vcf_index is not None:

            with tbi_path.open("wb") as file:
                shutil.copyfileobj(
                    vcf_index.file,
                    file,
                )

        else:

            try:
                subprocess.run(
                    [
                        "wsl",
                        "tabix",
                        "-p",
                        "vcf",
                        _windows_to_wsl_path(vcf_path),
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

            except FileNotFoundError as exc:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "WSL or tabix is not available "
                        "for automatic VCF indexing."
                    ),
                ) from exc

            except subprocess.CalledProcessError as exc:

                error_message = (
                    exc.stderr.strip()
                    or exc.stdout.strip()
                    or "Unknown tabix error."
                )

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "VCF index could not be created. "
                        f"{error_message}"
                    ),
                ) from exc

        # --------------------------------------------------
        # Verify index
        # --------------------------------------------------

        if not tbi_path.exists():
            raise HTTPException(
                status_code=400,
                detail=(
                    "VCF index (.tbi) could not be created."
                ),
            )

        # --------------------------------------------------
        # Discover VCF sample ID automatically
        # --------------------------------------------------

        vcf_sample_id = _get_vcf_sample_id(
            vcf_path
        )

        # --------------------------------------------------
        # Calculate all configured PRS models
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
                    sample_id=vcf_sample_id,
                    max_variants=model.get(
                        "development_limit"
                    ),
                    match_type=model[
                        "match_type"
                    ],
                )

                # Override the application-facing ID.
                #
                # The calculation itself uses the
                # VCF's internal sample ID.
                result["patient_id"] = patient_id

                # Keep the biological VCF sample ID
                # visible for traceability.
                result["vcf_sample_id"] = (
                    vcf_sample_id
                )

                results.append(result)

            except Exception as exc:

                results.append(
                    {
                        "disease": disease,
                        "patient_id": patient_id,
                        "vcf_sample_id": vcf_sample_id,
                        "pgs_id": model["pgs_id"],
                        "status": "ERROR",
                        "error": str(exc),
                    }
                )

        # --------------------------------------------------
        # Save results to PostgreSQL
        # --------------------------------------------------

        db = SessionLocal()

        try:

            for result in results:

                if result.get("status") == "ERROR":
                    continue

                existing_score = (
                    db.query(PRSScore)
                    .filter(
                        PRSScore.patient_id
                        == patient_id,
                        PRSScore.disease
                        == result["disease"],
                    )
                    .first()
                )

                if existing_score:

                    existing_score.raw_prs = (
                        result["prs"]
                    )

                    existing_score.score_100 = (
                        result["score_100"]
                    )

                    existing_score.score_100_status = (
                        result["score_100_status"]
                    )

                    existing_score.score_100_reference = (
                        result["score_100_reference"]
                    )

                else:

                    db.add(
                        PRSScore(
                            patient_id=patient_id,
                            disease=result["disease"],
                            raw_prs=result["prs"],
                            score_100=result["score_100"],
                            score_100_status=result[
                                "score_100_status"
                            ],
                            score_100_reference=result[
                                "score_100_reference"
                            ],
                        )
                    )

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        # --------------------------------------------------
        # Return results
        # --------------------------------------------------

        return {
            "patient_id": patient_id,
            "vcf_sample_id": vcf_sample_id,
            "diseases_processed": len(results),
            "results": results,
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    finally:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True,
        )