
import json

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
        analysis_status="candidate_for_review" if result["recommendations"] else "review_required",
        review_message=(
            "Demo output only. Variant annotation is not a validated diplotype or clinical advice; confirm results with a qualified pharmacogenomics professional."
        ),
        detected_variants=result["pharmacogene_variants"].get("CYP2C19", []),
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
    Accept a VCF file and analyze its parsed variants.

    medications_json must be a JSON array, for example:
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

    # Annotate each parsed variant using MyVariant.info.
    # Annotation supplies gene evidence; it does not call star alleles.
    annotated_variants = []

    for item in variants_data:
        annotation = annotate_parsed_variant(item)

        print("VARIANT:", item)
        print("ANNOTATION:", annotation)

        if (
            annotation.get("status") == "success"
            and annotation.get("gene")
        ):
            item["gene"] = annotation["gene"]

        annotated_variants.append(
            VariantInput.model_validate(item).model_dump()
        )

    print("ANNOTATED VARIANTS:", annotated_variants)

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
        analysis_status="candidate_for_review" if result["recommendations"] else "review_required",
        review_message=(
            "Demo output only. Variant annotation is not a validated diplotype or clinical advice; confirm results with a qualified pharmacogenomics professional."
        ),
        detected_variants=result["pharmacogene_variants"].get("CYP2C19", []),
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
