import json
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from .schema import (
    PharmacogenomicsRequest,
    PharmacogenomicsResponse,
    MedicationInput,
    VariantInput,
)
from .services.pipeline import run_pharmacogenomics_pipeline
from .services.variant_annotator import annotate_parsed_variant
from .services.vcf_parser import (
    MAX_VCF_SIZE_BYTES,
    VCFParseError,
    parse_vcf_content,
)
from .services.pharmcat_service import run_pharmcat


router = APIRouter(
    prefix="/pharmacogenomics",
    tags=["Pharmacogenomics"],
)


def summarize_pharmcat_report(report: dict[str, Any]) -> dict[str, Any]:
    """
    Extract a compact summary from PharmCAT's report JSON.

    Uncalled haplotypes are reported as uncertain information.
    They are not treated as confirmed missing variants.
    """

    genes_result = {}

    for gene_symbol, gene_data in report.get("genes", {}).items():
        diplotypes = []

        calls = gene_data.get("recommendationDiplotypes") or []

        for call in calls:
            diplotypes.append(
                {
                    "diplotype": call.get("label"),
                    "phenotypes": call.get("phenotypes") or [],
                    "activity_score": call.get("activityScore"),
                    "inferred": call.get("inferred"),
                    "match_score": call.get("matchScore"),
                }
            )

        warnings = []

        for message in gene_data.get("messages", []):
            if isinstance(message, dict):
                warnings.append(message)
            else:
                warnings.append(str(message))

        for variant in gene_data.get("variants", []):
            for warning in variant.get("warnings", []):
                warnings.append(
                    {
                        "variant": variant.get("dbSnpId"),
                        "position": variant.get("position"),
                        "message": warning,
                    }
                )

            if variant.get("hasUndocumentedVariations"):
                warnings.append(
                    {
                        "variant": variant.get("dbSnpId"),
                        "position": variant.get("position"),
                        "message": (
                            "Undocumented variation information "
                            "was reported by PharmCAT."
                        ),
                    }
                )

        uncalled_haplotypes = gene_data.get(
            "uncalledHaplotypes", []
        )

        # Include genes with a call or information requiring review.
        if diplotypes or warnings or uncalled_haplotypes:
            genes_result[gene_symbol] = {
                "diplotypes": diplotypes,
                "uncalled_haplotypes": uncalled_haplotypes,
                "warnings": warnings,
                "call_source": gene_data.get("callSource"),
            }

    return {
        "pharmcat_version": report.get("pharmcatVersion"),
        "report_title": report.get("title"),
        "genes": genes_result,
    }


@router.get("/ping")
async def ping():
    return {
        "module": "pharmacogenomics",
        "status": "ok",
        "message": "Pharmacogenomics Module 5 is running",
    }


@router.post(
    "/analyze",
    response_model=PharmacogenomicsResponse,
)
async def analyze_pharmacogenomics(
    request: PharmacogenomicsRequest,
):
    """Analyze variants supplied as JSON."""

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
        analysis_status=(
            "candidate_for_review"
            if result["recommendations"]
            else "review_required"
        ),
        review_message=(
            "Demo output only. Variant annotation is not a validated "
            "diplotype or clinical advice. Confirm results with a "
            "qualified pharmacogenomics professional."
        ),
        detected_variants=(
            result["pharmacogene_variants"].get("CYP2C19", [])
        ),
        diplotypes=result["diplotypes"],
        phenotypes=result["phenotypes"],
        recommendations=result["recommendations"],
        flagged_conflicts=result["flagged_conflicts"],
        confidence=result["confidence"],
        specialist=(
            "Clinical Pharmacist"
            if result["flagged_conflicts"]
            else None
        ),
    )


@router.post(
    "/analyze-vcf",
    response_model=PharmacogenomicsResponse,
)
async def analyze_vcf(
    patient_id: str = Form(...),
    medications_json: str = Form(...),
    clinical_indication: str = Form(""),
    file: UploadFile = File(...),
):
    """
    Parse a VCF, run PharmCAT through the separate worker,
    and run the existing GeneGuard pharmacogenomics pipeline.

    medications_json example:
    [{"name": "Clopidogrel", "dosage": "75 mg"}]
    """

    filename = (file.filename or "").lower()

    if not filename.endswith(".vcf"):
        raise HTTPException(
            status_code=400,
            detail="Upload a VCF file with a .vcf extension.",
        )

    try:
        content = await file.read(MAX_VCF_SIZE_BYTES + 1)

        if len(content) > MAX_VCF_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="The VCF file exceeds the 20 MB limit.",
            )

        variants_data = parse_vcf_content(content)

    except VCFParseError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()

    try:
        medications_data = json.loads(medications_json)

        if not isinstance(medications_data, list):
            raise ValueError("Medications must be a JSON array.")

        medications = [
            MedicationInput.model_validate(item)
            for item in medications_data
        ]

    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid medications_json. Supply a JSON array "
                'such as [{"name":"Clopidogrel","dosage":"75 mg"}].'
            ),
        ) from exc

    # Run PharmCAT through the shared-folder worker.
    try:
        pharmcat_report = await run_pharmcat(content)
        pharmcat_result = summarize_pharmcat_report(
            pharmcat_report
        )

    except (RuntimeError, TimeoutError, ValueError, OSError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"PharmCAT analysis failed: {str(exc)}",
        ) from exc

    # Run the existing MyVariant.info annotation.
    annotated_variants = []

    for item in variants_data:
        annotation = annotate_parsed_variant(item)

        if (
            annotation.get("status") == "success"
            and annotation.get("gene")
        ):
            item["gene"] = annotation["gene"]

        annotated_variants.append(
            VariantInput.model_validate(item).model_dump()
        )

    # Preserve the existing GeneGuard pipeline.
    result = await run_pharmacogenomics_pipeline(
        variants=annotated_variants,
        medications=[
            medication.model_dump()
            for medication in medications
        ],
        clinical_indication=clinical_indication or None,
    )

    return PharmacogenomicsResponse(
        patient_id=patient_id,
        analysis_status=(
            "candidate_for_review"
            if result["recommendations"]
            else "review_required"
        ),
        review_message=(
            "PharmCAT results and GeneGuard pipeline output are "
            "provided for review. Missing or uncalled haplotypes "
            "may affect interpretation. This is not a validated "
            "clinical result; confirm findings with a qualified "
            "pharmacogenomics professional."
        ),
        detected_variants=(
            result["pharmacogene_variants"].get("CYP2C19", [])
        ),
        diplotypes=result["diplotypes"],
        phenotypes=result["phenotypes"],
        recommendations=result["recommendations"],
        flagged_conflicts=result["flagged_conflicts"],
        confidence=result["confidence"],
        specialist=(
            "Clinical Pharmacist"
            if result["flagged_conflicts"]
            else None
        ),
        pharmcat_result=pharmcat_result,
    )