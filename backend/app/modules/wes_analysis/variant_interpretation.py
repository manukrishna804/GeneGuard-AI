from .interpretation_config import SNV_THRESHOLDS
from .snv_criteria import evaluate_snv_criteria


def interpret_variant(
    variant_record,
    combined_evidence
):
    """
    Create a structured interpretation for a variant.

    Clinical classification is intentionally conservative.
    The current engine summarizes available evidence but does
    not assign a clinical Pathogenic/Likely Pathogenic/Benign
    classification from computational evidence alone.
    """

    variant_type = variant_record.get("type")
    criteria = None

    interpretation = {
        "classification": "VUS",
        "confidence": "low",
        "reasoning": [],
        "variant": {
            "gene": variant_record.get("gene"),
            "variant": variant_record.get("variant"),
            "type": variant_type
        }
    }

    # ========================================================
    # SNV
    # ========================================================

    if variant_type == "SNV":

        identity = combined_evidence.get(
            "identity",
            {}
        ) or {}

        evidence = combined_evidence.get(
            "evidence",
            {}
        ) or {}

        consequence = evidence.get(
            "consequence"
        ) or {}

        predictions = evidence.get(
            "computational_predictions"
        ) or {}

        conservation = evidence.get(
            "conservation"
        ) or {}

        sources = evidence.get(
            "sources"
        ) or {}

        clingen = identity.get(
            "clingen"
        ) or {}

        clinvar = evidence.get(
            "clinvar"
        ) or {
            "status": "not_available",
            "records": []
        }
        
        criteria = evaluate_snv_criteria(
            consequence=consequence,
            computational_predictions=predictions,
            clinvar=clinvar,
            clingen=clingen,
            validation_sources=sources,
            population=evidence.get("population") or {},
        )

        # --------------------------------------------
        # Identity
        # --------------------------------------------

        interpretation["identity"] = {
            "transcript": identity.get(
                "transcript"
            ),
            "protein": identity.get(
                "protein"
            ),
            "genomic": identity.get(
                "genomic"
            ),
            "clingen_caid": clingen.get(
                "caid"
            )
        }

        # --------------------------------------------
        # Evidence summary
        # --------------------------------------------

        interpretation["evidence_summary"] = {
            "consequence": consequence,
            "computational_predictions": predictions,
            "conservation": conservation,
            "clingen": clingen,
            "clinvar": clinvar,
            "criteria": criteria,
            "sources": sources
        }

        # --------------------------------------------
        # Evidence reasoning
        # --------------------------------------------

        supporting = []

        effect = consequence.get(
            "effect"
        )

        if effect == "missense_variant":
            supporting.append(
                "Variant is a missense change."
            )

        # CADD
        cadd = predictions.get(
            "cadd"
        )

        if isinstance(cadd, (int, float)):

            if cadd >= SNV_THRESHOLDS[
                "cadd_high"
            ]:
                supporting.append(
                    f"CADD score is {cadd}, which is above "
                    "the configured high-impact threshold."
                )

        # REVEL
        revel_values = predictions.get(
            "revel",
            []
        ) or []

        numeric_revel = [
            value
            for value in revel_values
            if isinstance(value, (int, float))
        ]

        if numeric_revel:

            max_revel = max(
                numeric_revel
            )

            if max_revel >= SNV_THRESHOLDS[
                "revel_damaging"
            ]:
                supporting.append(
                    f"REVEL score is {max_revel}, "
                    "supporting a damaging prediction."
                )

        # SIFT
        sift_values = predictions.get(
            "sift",
            []
        ) or []

        if any(
            str(value).upper() == "D"
            for value in sift_values
        ):
            supporting.append(
                "SIFT contains a damaging prediction."
            )

        # PolyPhen
        polyphen = predictions.get(
            "polyphen",
            {}
        ) or {}

        if any(
            str(value).upper() == "D"
            for prediction_set in polyphen.values()
            if isinstance(prediction_set, list)
            for value in prediction_set
        ):
            supporting.append(
                "PolyPhen contains a damaging prediction."
            )

        # VariantValidator
        if (
            sources.get(
                "variantvalidator",
                {}
            ).get("status")
            == "validated"
        ):
            supporting.append(
                "VariantValidator successfully validated "
                "the normalized variant."
            )

        # ClinGen
        if clingen.get(
            "status"
        ) == "found":
            supporting.append(
                "ClinGen Allele Registry returned a "
                "matching allele identity."
            )

        # ClinVar
        if clinvar.get(
            "status"
        ) == "found":
            supporting.append(
                "ClinVar records were found for the variant."
            )

        interpretation["reasoning"] = supporting

        # --------------------------------------------
        # Current classification policy
        # --------------------------------------------

        interpretation["classification"] = "VUS"
        interpretation["confidence"] = "low"

        interpretation["reasoning"].append(
            "Current SNV engine does not assign a clinical "
            "Pathogenic/Likely Pathogenic/Benign classification "
            "from computational evidence alone."
        )

    # ========================================================
    # CNV
    # ========================================================

    elif variant_type == "CNV":

        identity = combined_evidence.get(
            "identity",
            {}
        ) or {}

        evidence = combined_evidence.get(
            "evidence",
            {}
        ) or {}

        dbvar = evidence.get(
            "dbvar",
            {}
        ) or {}

        sources = evidence.get(
            "sources"
        ) or {}

        # --------------------------------------------
        # Identity
        # --------------------------------------------

        interpretation["identity"] = {
            "normalization": identity.get(
                "normalization"
            ),
            "assembly": identity.get(
                "assembly"
            ),
            "search_region": identity.get(
                "search_region"
            )
        }

        # --------------------------------------------
        # Evidence summary
        # --------------------------------------------

        interpretation["evidence_summary"] = {
            "dbvar_match_status": dbvar.get(
                "match_status"
            ),
            "dbvar_candidates": dbvar.get(
                "candidates",
                []
            ),
            "sources": sources,
            "criteria": criteria
        }

        # --------------------------------------------
        # Evidence reasoning
        # --------------------------------------------

        match_status = dbvar.get(
            "match_status"
        )

        if match_status == "exact":
            interpretation["reasoning"].append(
                "A type-relevant dbVar candidate has an "
                "exact coordinate match."
            )

        elif match_status == "overlap":
            interpretation["reasoning"].append(
                "A type-relevant dbVar candidate overlaps "
                "the reported CNV coordinates."
            )

        elif match_status == "not_found":
            interpretation["reasoning"].append(
                "No type-relevant dbVar candidate was found."
            )

        else:
            interpretation["reasoning"].append(
                "CNV evidence has been collected, but no "
                "specific coordinate classification was established."
            )

        interpretation["reasoning"].append(
            "Current CNV engine does not assign a clinical "
            "Pathogenic/Likely Pathogenic/Benign classification "
            "from dbVar coordinate evidence alone."
        )

        # --------------------------------------------
        # Current classification policy
        # --------------------------------------------

        interpretation["classification"] = "VUS"
        interpretation["confidence"] = "low"

    # ========================================================
    # UNKNOWN TYPE
    # ========================================================

    else:

        interpretation["classification"] = (
            "unsupported"
        )

        interpretation["confidence"] = (
            "none"
        )

        interpretation["reasoning"].append(
            "Unsupported variant type."
        )

    return interpretation