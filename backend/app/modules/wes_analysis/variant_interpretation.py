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

    if variant_type == "SNV":

        identity = combined_evidence.get(
            "identity",
            {}
        )

        evidence = combined_evidence.get(
            "evidence",
            {}
        )

        consequence = evidence.get(
            "consequence",
            {}
        )

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
            "computational_predictions": evidence.get(
                "computational_predictions",
                {}
            ),
            "conservation": evidence.get(
                "conservation",
                {}
            ),
            "sources": evidence.get(
                "sources",
                {}
            )
        }

        interpretation["reasoning"].append(
            "Variant evidence has been collected, "
            "but clinical classification rules have not "
            "yet been applied."
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