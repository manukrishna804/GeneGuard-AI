from __future__ import annotations

from typing import Any


def build_intervention_recommendations(
    condition: str | None,
    inheritance: str | None,
    classification: str | None,
) -> dict[str, Any]:
    """
    Build evidence-aware preconception options from an assessed
    genetic risk.

    This function provides decision-support information only.
    It does not diagnose disease, prescribe treatment, or determine
    which reproductive option a couple should choose.
    """

    recommendations: list[dict[str, Any]] = []

    normalized_inheritance = (inheritance or "").lower()
    normalized_classification = (classification or "").lower()

    # These findings require clinical confirmation before
    # reproductive decision-making.
    if normalized_classification in {
        "pathogenic",
        "likely_pathogenic",
    }:
        recommendations.append(
            {
                "option": "Genetic counselling",
                "reason": (
                    "Discuss the confirmed or suspected disease-causing "
                    "variant, inheritance pattern, and reproductive implications "
                    "with a qualified genetic counselor or clinical geneticist."
                ),
            }
        )

        recommendations.append(
            {
                "option": "Confirmatory parental testing",
                "reason": (
                    "Confirm the relevant parental variant(s) using an "
                    "appropriate clinical laboratory test before making "
                    "reproductive decisions."
                ),
            }
        )

    # PGT-M is relevant primarily when a specific monogenic condition
    # and familial disease-causing variant have been established.
    if normalized_inheritance in {
        "autosomal_recessive",
        "autosomal_dominant",
        "x_linked_recessive",
    }:
        recommendations.append(
            {
                "option": "Discuss IVF with PGT-M",
                "reason": (
                    "For an established monogenic condition with a known "
                    "familial disease-causing variant, preimplantation "
                    "genetic testing for monogenic disease (PGT-M) may be "
                    "an option to discuss with a reproductive specialist."
                ),
            }
        )

        recommendations.append(
            {
                "option": "Discuss prenatal diagnostic testing",
                "reason": (
                    "If pregnancy occurs, diagnostic testing such as "
                    "chorionic-villus sampling or amniocentesis may be "
                    "considered when clinically appropriate."
                ),
            }
        )

    # VUS should not be treated as an established disease-causing finding.
    if normalized_classification in {
        "uncertain",
        "vus",
        "variant_of_uncertain_significance",
    }:
        recommendations.append(
            {
                "option": "Clinical variant review",
                "reason": (
                    "A variant of uncertain significance should not be "
                    "used alone to make definitive reproductive decisions. "
                    "Clinical review and possible future re-evaluation "
                    "are appropriate."
                ),
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "option": "Clinical genetic assessment",
                "reason": (
                    "The available computational evidence is insufficient "
                    "to determine a specific reproductive intervention. "
                    "Further clinical and laboratory evaluation is recommended."
                ),
            }
        )

    return {
        "condition": condition or "Unknown condition",
        "inheritance": inheritance or "Unknown",
        "classification": classification or "Unknown",
        "recommendations": recommendations,
        "disclaimer": (
            "These are decision-support options, not medical prescriptions "
            "or a clinical diagnosis. Reproductive and treatment decisions "
            "should be made with qualified healthcare professionals."
        ),
    }