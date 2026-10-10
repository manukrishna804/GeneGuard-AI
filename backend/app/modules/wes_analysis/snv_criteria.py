from .interpretation_config import SNV_THRESHOLDS
def evaluate_pp3_candidate(computational_predictions):
    """
    Evaluate whether computational evidence is sufficient to make
    PP3 a candidate.

    This does not apply PP3 clinically.
    """

    computational_predictions = computational_predictions or {}

    supporting = []

    cadd = computational_predictions.get("cadd")

    if (
        isinstance(cadd, (int, float))
        and cadd >= SNV_THRESHOLDS["cadd_high"]
    ):
        supporting.append({
            "tool": "CADD",
            "value": cadd,
            "threshold": SNV_THRESHOLDS["cadd_high"]
        })

    revel = computational_predictions.get("revel")

    if revel:
        revel_values = (
            revel if isinstance(revel, list)
            else [revel]
        )

        numeric_revel = [
            value
            for value in revel_values
            if isinstance(value, (int, float))
        ]

        if (
            numeric_revel
            and max(numeric_revel)
            >= SNV_THRESHOLDS["revel_damaging"]
        ):
            supporting.append({
                "tool": "REVEL",
                "value": max(numeric_revel),
                "threshold": SNV_THRESHOLDS["revel_damaging"]
            })

    if len(supporting) >= 2:
        return {
            "status": "candidate",
            "evidence": supporting
        }

    return {
        "status": "insufficient",
        "evidence": supporting
    }
def evaluate_bp4_candidate(computational_predictions):
    """
    Evaluate whether computational evidence is sufficiently benign
    to make BP4 a candidate.

    This does not apply BP4 clinically.
    """

    computational_predictions = computational_predictions or {}

    supporting = []

    sift = computational_predictions.get("sift")

    if isinstance(sift, list):
        sift_values = [
            str(value).upper()
            for value in sift
        ]

        if sift_values and all(
            value in {"T", "N"}
            for value in sift_values
        ):
            supporting.append({
                "tool": "SIFT",
                "value": sift_values,
                "interpretation": "benign"
            })

    polyphen = computational_predictions.get("polyphen")

    if isinstance(polyphen, dict):
        polyphen_values = []

        for values in polyphen.values():
            if isinstance(values, list):
                polyphen_values.extend(
                    str(value).upper()
                    for value in values
                )
            else:
                polyphen_values.append(
                    str(values).upper()
                )

        if polyphen_values and all(
            value == "B"
            for value in polyphen_values
        ):
            supporting.append({
                "tool": "PolyPhen",
                "value": polyphen_values,
                "interpretation": "benign"
            })

    return {
        "status": (
            "candidate"
            if len(supporting) >= 2
            else "insufficient"
        ),
        "evidence": supporting
    }
def summarize_criteria(criteria):
    """
    Summarize ACMG criterion candidates and evidence availability.
    """

    criteria = criteria or {}

    formal = criteria.get("formal_acmg_criteria", [])
    observations = criteria.get("evidence_observations", [])
    unavailable = criteria.get("unavailable", [])

    return {
        "candidate_count": len(formal),
        "candidate_criteria": [
            item.get("criterion")
            for item in formal
            if item.get("status") == "candidate"
        ],
        "observation_count": len(observations),
        "unavailable_count": len(unavailable),
        "clinical_classification_applied": (
            criteria.get("metadata", {})
            .get("clinical_classification_applied", False)
        )
    }
def evaluate_snv_criteria(
    consequence,
    computational_predictions,
    clinvar,
    clingen,
    validation_sources,
    population,
):
    """
    Organize SNV evidence into:
    - formal_acmg_criteria
    - evidence_observations
    - unavailable

    This function does NOT assign a clinical classification.
    """

    consequence = consequence or {}
    computational_predictions = computational_predictions or {}
    clinvar = clinvar or {}
    clingen = clingen or {}
    validation_sources = validation_sources or {}
    population = population or {}

    formal_acmg_criteria = []
    evidence_observations = []
    unavailable = []

    metadata = {
        "clinical_classification_applied": False
    }

    # ---------------------------------------------------------
    # Consequence
    # ---------------------------------------------------------

    effect = consequence.get("effect")

    if effect:
        evidence_observations.append({
            "observation": "CONSEQUENCE",
            "value": effect,
            "description": "Variant consequence reported by the evidence source.",
            "source": "MyVariant.info"
        })
    else:
        unavailable.append({
            "evidence": "CONSEQUENCE",
            "description": "No variant consequence was available."
        })

    # A missense consequence by itself is NOT an ACMG
    # pathogenic or benign criterion.
    if effect == "missense_variant":
        evidence_observations.append({
            "observation": "MISSENSE_VARIANT",
            "value": True,
            "description": "Variant is annotated as a missense change.",
            "source": "MyVariant.info"
        })

    # ---------------------------------------------------------
    # Computational evidence observations
    # ---------------------------------------------------------

    cadd = computational_predictions.get("cadd")

    if isinstance(cadd, (int, float)):
        evidence_observations.append({
            "observation": "CADD",
            "value": cadd,
            "description": "CADD computational prediction is available.",
            "source": "MyVariant.info"
        })
    else:
        unavailable.append({
            "evidence": "CADD",
            "description": "CADD prediction was not available."
        })

    revel = computational_predictions.get("revel")

    if revel:
        evidence_observations.append({
            "observation": "REVEL",
            "value": revel,
            "description": "REVEL computational prediction is available.",
            "source": "MyVariant.info"
        })
    else:
        unavailable.append({
            "evidence": "REVEL",
            "description": "REVEL prediction was not available."
        })

    sift = computational_predictions.get("sift")

    if sift:
        evidence_observations.append({
            "observation": "SIFT",
            "value": sift,
            "description": "SIFT computational prediction is available.",
            "source": "MyVariant.info"
        })
    else:
        unavailable.append({
            "evidence": "SIFT",
            "description": "SIFT prediction was not available."
        })

    polyphen = computational_predictions.get("polyphen")

    if polyphen:
        evidence_observations.append({
            "observation": "POLYPHEN",
            "value": polyphen,
            "description": "PolyPhen computational prediction is available.",
            "source": "MyVariant.info"
        })
    else:
        unavailable.append({
            "evidence": "POLYPHEN",
            "description": "PolyPhen prediction was not available."
        })
        # ---------------------------------------------------------
    # PP3 candidate
    # ---------------------------------------------------------

        # ---------------------------------------------------------
    # PP3 candidate
    # ---------------------------------------------------------

    pp3 = evaluate_pp3_candidate(
        computational_predictions
    )

    if pp3["status"] == "candidate":
        formal_acmg_criteria.append({
            "criterion": "PP3",
            "status": "candidate",
            "strength": None,
            "supporting_predictions": pp3["evidence"],
            "description": (
                "Multiple configured computational predictors support "
                "a potentially damaging effect; formal PP3 application "
                "requires review under the selected evidence model."
            )
        })
        # ---------------------------------------------------------
    # BP4 candidate
    # ---------------------------------------------------------

    bp4 = evaluate_bp4_candidate(
        computational_predictions
    )

    if bp4["status"] == "candidate":
        formal_acmg_criteria.append({
            "criterion": "BP4",
            "status": "candidate",
            "strength": None,
            "supporting_predictions": bp4["evidence"],
            "description": (
                "Multiple computational predictors support a "
                "potentially benign effect; formal BP4 application "
                "requires review under the selected evidence model."
            )
        })
    # ---------------------------------------------------------
    # Validation / identity observations
    # ---------------------------------------------------------

    variantvalidator = validation_sources.get("variantvalidator") or {}

    if variantvalidator.get("status") == "validated":
        metadata["variant_validator_validated"] = True

        evidence_observations.append({
            "observation": "VARIANTVALIDATOR_VALIDATED",
            "value": True,
            "description": "Normalized variant was successfully validated.",
            "source": "VariantValidator"
        })
    else:
        unavailable.append({
            "evidence": "VARIANTVALIDATOR",
            "description": "VariantValidator validation was not available."
        })

    if clingen.get("status") == "found":
        metadata["clingen_allele_identified"] = True

        evidence_observations.append({
            "observation": "CLINGEN_ALLELE",
            "value": clingen.get("caid"),
            "description": "ClinGen Allele Registry identified the variant allele.",
            "source": "ClinGen Allele Registry"
        })
    else:
        unavailable.append({
            "evidence": "CLINGEN",
            "description": "ClinGen allele identity was not available."
        })

    # ---------------------------------------------------------
    # ClinVar
    # ---------------------------------------------------------

    if clinvar.get("status") == "found":
        metadata["clinvar_record_found"] = True

        evidence_observations.append({
            "observation": "CLINVAR_RECORD",
            "value": clinvar.get("records", []),
            "description": "ClinVar records were found for the variant.",
            "source": "ClinVar"
        })
    else:
        unavailable.append({
            "evidence": "CLINVAR",
            "description": "No ClinVar record was found."
        })
        # ---------------------------------------------------------
    # Population frequency
    # ---------------------------------------------------------

    population_status = population.get("status")

    if population_status == "found":
        evidence_observations.append({
            "observation": "GNOMAD_POPULATION",
            "value": {
                "allele_frequency": population.get("allele_frequency"),
                "allele_count": population.get("allele_count"),
                "allele_number": population.get("allele_number"),
                "homozygote_count": population.get("homozygote_count"),
            },
            "description": "gnomAD population-frequency data are available.",
            "source": "gnomAD"
        })

    elif population_status == "not_found":
        evidence_observations.append({
            "observation": "GNOMAD_NOT_FOUND",
            "value": True,
            "description": "Variant was not found in the queried gnomAD dataset.",
            "source": "gnomAD"
        })

        formal_acmg_criteria.append({
            "criterion": "PM2",
            "status": "candidate",
            "strength": None,
            "description": (
                "Variant was not found in the queried gnomAD dataset; "
                "additional population-database and coverage checks are "
                "required before applying PM2."
            ),
            "source": "gnomAD"
        })

    else:
        unavailable.append({
            "evidence": "GNOMAD",
            "description": "Population-frequency evidence was unavailable."
        })

    result = {
        "formal_acmg_criteria": formal_acmg_criteria,
        "evidence_observations": evidence_observations,
        "unavailable": unavailable,
        "metadata": metadata,
    }

    result["summary"] = summarize_criteria(result)

    return result