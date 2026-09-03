import json

from .pdf_extractor import extract_text_from_pdf
from .variant_extractor import extract_variant_records
from .variant_validator import validate_variant
from .variant_evidence import get_variant_evidence
from .evidence_combiner import combine_evidence
from .variant_interpretation import interpret_variant


# ============================================================
# FULL WES ANALYSIS PIPELINE
# ============================================================

def analyze_wes_report(pdf_path):

    # --------------------------------------------------------
    # STAGE 1: PDF -> TEXT
    # --------------------------------------------------------

    text = extract_text_from_pdf(pdf_path)

    # --------------------------------------------------------
    # STAGE 2: TEXT -> VARIANT RECORDS
    # --------------------------------------------------------

    variant_records = extract_variant_records(text)

    results = []

    # --------------------------------------------------------
    # PROCESS EACH VARIANT
    # --------------------------------------------------------

    for record in variant_records:

        # ----------------------------------------------------
        # STAGE 3: BASIC VALIDATION
        # ----------------------------------------------------

        validation = validate_variant(record)

        if not validation["valid"]:

            results.append({
                "variant": record,
                "status": "invalid",
                "validation": validation
            })

            continue

        # ----------------------------------------------------
        # STAGE 4: EXTERNAL EVIDENCE
        # ----------------------------------------------------

        evidence = get_variant_evidence(record)

        # ----------------------------------------------------
        # STAGE 5: COMBINE
        # ----------------------------------------------------

        combined = combine_evidence(
            variant_record=record,
            validation_result=validation,
            evidence_result=evidence
        )

        interpretation = interpret_variant(
            variant_record=record,
            combined_evidence=combined
        )
        combined["interpretation"] = interpretation

        results.append(combined)

    return results


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    pdf_path = "medgenome_report.pdf"

    results = analyze_wes_report(
        pdf_path
    )

    print("\n==========================================")
    print("FINAL WES ANALYSIS")
    print("==========================================")

    print(
        json.dumps(
            results,
            indent=4
        )
    )