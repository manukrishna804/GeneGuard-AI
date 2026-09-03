import json


# ============================================================
# STAGE 5: EVIDENCE COMBINATION
# ============================================================

def combine_evidence(
    variant_record,
    validation_result,
    evidence_result
):
    """
    Combine the original variant, basic validation,
    and external evidence into one clean structure.
    """

    variant_type = variant_record.get("type")

    # ========================================================
    # COMMON INFORMATION
    # ========================================================

    combined = {
        "gene": variant_record.get("gene"),
        "variant": variant_record.get("variant"),
        "type": variant_type,

        "validation": {
            "valid": validation_result.get("valid"),
            "errors": validation_result.get("errors", []),
            "warnings": validation_result.get("warnings", [])
        },

        "evidence": {}
    }

    # ========================================================
    # SNV
    # ========================================================

    if variant_type == "SNV":

        validator = evidence_result.get(
            "variantvalidator",
            {}
        )

        normalization = evidence_result.get(
            "normalization",
            {}
        )

        myvariant = evidence_result.get(
            "myvariant",
            {}
        )
        clingen = evidence_result.get(
            "clingen",
            {}
        )

        # --------------------------------------------
        # Identity / normalized representation
        # --------------------------------------------

        combined["identity"] = {
            "normalization": normalization,
            "input_hgvs": validator.get(
                "input_hgvs"
            ),

            "transcript": validator.get(
                "transcript"
            ),

            "protein": validator.get(
                "protein"
            ),

            "genomic": validator.get(
                "genomic"
            ),

            "assembly": validator.get(
                "assembly"
            ),

            "exon": validator.get(
                "exon"
            ),

            "vcf": validator.get(
                "vcf"
            ),

            "clingen": clingen,
        }

        # --------------------------------------------
        # Validation
        # --------------------------------------------

        combined["validation"]["external"] = {
            "variantvalidator": {
                "validated": validator.get(
                    "validated"
                ),

                "warnings": validator.get(
                    "warnings",
                    []
                )
            }
        }

        # --------------------------------------------
        # Functional consequence
        # --------------------------------------------

        consequence = myvariant.get(
            "consequence"
        )

        combined["evidence"]["consequence"] = (
            consequence
        )

        # --------------------------------------------
        # Computational predictions
        # --------------------------------------------

        combined["evidence"][
            "computational_predictions"
        ] = myvariant.get(
            "computational_predictions",
            {}
        )

        # --------------------------------------------
        # Conservation
        # --------------------------------------------

        combined["evidence"][
            "conservation"
        ] = myvariant.get(
            "conservation",
            {}
        )

        # --------------------------------------------
        # Source status
        # --------------------------------------------

        combined["evidence"]["sources"] = {
            "variantvalidator": {
                "status": (
                    "validated"
                    if validator.get("validated")
                    else "not_validated"
                )
            },

            "myvariant": {
                "status": (
                    "found"
                    if myvariant.get("found")
                    else "not_found"
                )
            },
            "clingen": {
                "status": clingen.get(
                    "status",
                    "not_available"
                )
            }
        }

    # ========================================================
    # CNV
    # ========================================================

    elif variant_type == "CNV":

        search_region = evidence_result.get(
            "search_region",
            {}
        )
        normalization = evidence_result.get(
            "normalization",
            {}
                )

        candidates = evidence_result.get(
            "dbvar_candidates",
            []
        )

        combined["identity"] = {
            "normalization": normalization,
            "assembly": "GRCh38",
            "search_region": search_region
        }

        # --------------------------------------------
        # dbVar evidence
        # --------------------------------------------

        candidate_match_status = "not_found"

        for candidate in candidates:

            if candidate.get("type_relevant") is not True:
                continue

            status = candidate.get("match_status")

            if status == "exact":
                candidate_match_status = "exact"
                break

            if status == "overlap":
                candidate_match_status = "overlap"

        combined["evidence"]["dbvar"] = {
            "search_status": (
                "found"
                if candidates
                else "not_found"
            ),
            "match_status": candidate_match_status,
            "candidates": candidates
        }

        # --------------------------------------------
        # Source status
        # --------------------------------------------

        combined["evidence"]["sources"] = {
            "dbvar": {
                "status": (
                    "candidate_found"
                    if candidates
                    else "not_found"
                ),

                "candidate_count": len(
                    candidates
                )
            }
        }

    # ========================================================
    # UNKNOWN TYPE
    # ========================================================

    else:

        combined["identity"] = {}

        combined["evidence"] = {
            "status": "unsupported_variant_type"
        }

    return combined


# ============================================================
# TEST USING ACTUAL PIPELINE
# ============================================================

if __name__ == "__main__":

    from pdf_extractor import extract_text_from_pdf
    from variant_extractor import extract_variant_records
    from variant_validator import validate_variant
    from variant_evidence import get_variant_evidence


    # --------------------------------------------------------
    # 1. EXTRACT PDF
    # --------------------------------------------------------

    pdf_path = "medgenome_report.pdf"

    print(
        "\nReading PDF..."
    )

    text = extract_text_from_pdf(
        pdf_path
    )


    # --------------------------------------------------------
    # 2. EXTRACT VARIANTS
    # --------------------------------------------------------

    print(
        "Extracting variants..."
    )

    records = extract_variant_records(
        text
    )


    # --------------------------------------------------------
    # 3. PROCESS EACH VARIANT
    # --------------------------------------------------------

    final_results = []

    for record in records:

        print(
            "\n------------------------------------------"
        )

        print(
            "Processing:",
            record
        )

        # --------------------------------------------
        # Basic validation
        # --------------------------------------------

        validation = validate_variant(
            record
        )

        # --------------------------------------------
        # Stop invalid variants
        # --------------------------------------------

        if not validation["valid"]:

            final_results.append({

                "gene": record.get(
                    "gene"
                ),

                "variant": record.get(
                    "variant"
                ),

                "type": record.get(
                    "type"
                ),

                "validation": validation,

                "status": "invalid"
            })

            continue

        # --------------------------------------------
        # External evidence
        # --------------------------------------------

        evidence = get_variant_evidence(
            record
        )

        # --------------------------------------------
        # Combine
        # --------------------------------------------

        combined = combine_evidence(

            variant_record=record,

            validation_result=validation,

            evidence_result=evidence
        )

        final_results.append(
            combined
        )


    # --------------------------------------------------------
    # 4. PRINT FINAL RESULT
    # --------------------------------------------------------

    print(
        "\n=========================================="
    )

    print(
        "FINAL EVIDENCE"
    )

    print(
        "=========================================="
    )

    print(
        json.dumps(
            final_results,
            indent=4
        )
    )