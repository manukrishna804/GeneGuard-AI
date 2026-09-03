from .interpretation_config import SNV_THRESHOLDS
def interpret_variant(
    variant_record,
    combined_evidence
):
    """
    Create a structured interpretation for a variant.

    This function currently prepares the interpretation structure.
    Clinical classification rules will be added in later steps.
    """

    variant_type = variant_record.get("type")

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

        # ========================================================
    # SNV
    # ========================================================

    if variant_type == "SNV":

        identity = combined_evidence.get(
            "identity",
            {}
        )

        evidence = combined_evidence.get(
            "evidence",
            {}
        )
        clingen_caid = identity.get(
            "clingen_caid"
        )

        consequence = evidence.get(
            "consequence"
        ) or {}

        predictions = evidence.get(
            "computational_predictions"
        ) or {}

        sources = evidence.get(
            "sources"
        ) or {}
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
            "clingen_caid": identity.get(
                "clingen_caid"
            )
        }

        interpretation["evidence_summary"] = {
            "consequence": consequence,
            "computational_predictions": predictions,
            "conservation": evidence.get(
                "conservation",
                {}
            ),
            "sources": sources,
            "clingen": identity.get(
                "clingen",
                {}
            )
        }

        # ----------------------------------------------------
        # Evidence counters
        # ----------------------------------------------------

        supporting = []
        conflicting = []

        # Consequence
        effect = consequence.get("effect")

        if effect == "missense_variant":
            supporting.append(
                "Variant is a missense change."
            )

        # CADD
        cadd = predictions.get("cadd")

        if isinstance(cadd, (int, float)):
            if cadd >= SNV_THRESHOLDS["cadd_high"]:
                supporting.append(
                    f"CADD score is {cadd}, which is above "
                    "the configured high-impact threshold."
                )

        # REVEL
        revel_values = predictions.get(
            "revel",
            []
        )

        if revel_values:
            numeric_revel = [
                value
                for value in revel_values
                if isinstance(value, (int, float))
            ]

            if numeric_revel:
                max_revel = max(numeric_revel)

                if max_revel >= SNV_THRESHOLDS["revel_damaging"]:
                    supporting.append(
                        f"REVEL score is {max_revel}, "
                        "supporting a damaging prediction."
                    )

        # SIFT
        sift_values = predictions.get(
            "sift",
            []
        )

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
        )

        if any(
            str(value).upper() == "D"
            for prediction_set in polyphen.values()
            for value in prediction_set
        ):
            supporting.append(
                "PolyPhen contains a damaging prediction."
            )

        # Source validation
        variantvalidator_status = sources.get(
            "variantvalidator",
            {}
        ).get("status")

        if variantvalidator_status == "validated":
            supporting.append(
                "VariantValidator successfully validated "
                "the normalized variant."
            )

        # ----------------------------------------------------
        # Current interpretation policy
        # ----------------------------------------------------

        interpretation["reasoning"] = supporting

        # IMPORTANT:
        # Evidence collected here is not sufficient by itself
        # to assign a clinical ACMG/AMP classification.

        if supporting:
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
        )

        evidence = combined_evidence.get(
            "evidence",
            {}
        )

        dbvar = evidence.get(
            "dbvar",
            {}
        )

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

        interpretation["evidence_summary"] = {
            "dbvar_match_status": dbvar.get(
                "match_status"
            ),
            "dbvar_candidates": dbvar.get(
                "candidates",
                []
            ),
            "sources": evidence.get(
                "sources",
                {}
            )
        }

        interpretation["reasoning"].append(
            "CNV evidence has been collected, "
            "but clinical classification rules have not "
            "yet been applied."
        )

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