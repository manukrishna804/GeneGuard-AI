from __future__ import annotations

from typing import List

from .compound_heterozygous import find_same_gene_different_variants
from .schemas import (
    ConsanguinityInfo,
    GeneticVariant,
    OffspringRiskAssessmentResponse,
    OffspringRiskResult,
    VariantRiskResult,
)


def build_assessment_response(
    risks: List[VariantRiskResult],
    consanguinity: ConsanguinityInfo | None = None,
    parent1_variants: List[GeneticVariant] | None = None,
    parent2_variants: List[GeneticVariant] | None = None,
) -> OffspringRiskAssessmentResponse:
    """
    Build the overall Module 4 offspring-risk assessment
    from individual variant-level risk results.
    """

    limitations = [
        "Risk calculations are based on the available variant "
        "annotations and the selected Mendelian inheritance model.",
        "Variants classified as VUS or without sufficient evidence "
        "are not used for definitive risk calculations.",
        "This computational assessment does not replace clinical "
        "genetic counseling or diagnostic evaluation.",
    ]

    # ---------------------------------------------------------
    # Convert VariantRiskResult -> OffspringRiskResult
    # ---------------------------------------------------------

    offspring_risks: List[OffspringRiskResult] = []

    for risk in risks:

        offspring_risks.append(
            OffspringRiskResult(
                gene=risk.gene,
                condition=(
                    risk.condition
                    or "Unknown condition"
                ),
                inheritance=(
                    risk.inheritance
                    or "unknown"
                ),
                parent1_status=risk.parent1_status,
                parent2_status=risk.parent2_status,
                affected_probability=risk.affected_probability,
                carrier_probability=risk.carrier_probability,
                unaffected_probability=risk.unaffected_probability,
                evidence_sources=risk.evidence_sources,
                explanation=(
                    risk.explanation
                    or "No explanation available."
                ),
            )
        )

    # ---------------------------------------------------------
    # Consanguinity context
    # ---------------------------------------------------------

    consanguinity_context = None

    if consanguinity is not None:

        if consanguinity.relationship.value == "unrelated":

            consanguinity_context = (
                "No consanguineous relationship was reported."
            )

        elif consanguinity.relationship.value == "first_cousin":

            consanguinity_context = (
                "A first-cousin relationship was reported. "
                "This is considered contextual information and "
                "is not applied as a fixed multiplier to the "
                "calculated Mendelian probabilities."
            )

        elif consanguinity.relationship.value == "second_cousin":

            consanguinity_context = (
                "A second-cousin relationship was reported. "
                "This is considered contextual information and "
                "is not applied as a fixed multiplier to the "
                "calculated Mendelian probabilities."
            )

        elif consanguinity.relationship.value == "other":

            description = (
                consanguinity.description
                or "A consanguineous relationship was reported."
            )

            consanguinity_context = (
                f"{description} This information is treated as "
                "contextual information rather than as a fixed "
                "risk multiplier."
            )

        else:

            consanguinity_context = (
                "The consanguinity relationship was not specified."
            )

    # ---------------------------------------------------------
    # Detect potential compound heterozygous candidates
    # ---------------------------------------------------------

    compound_candidates: List[str] = []

    if (
        parent1_variants is not None
        and parent2_variants is not None
    ):

        candidates = find_same_gene_different_variants(
            parent1_variants,
            parent2_variants,
        )

        for parent1_variant, parent2_variant in candidates:

            description = (
                f"{parent1_variant.gene}: "
                f"Parent 1 variant "
                f"{parent1_variant.variant_name or 'unknown'} "
                f"at {parent1_variant.chromosome}:"
                f"{parent1_variant.position} and "
                f"Parent 2 variant "
                f"{parent2_variant.variant_name or 'unknown'} "
                f"at {parent2_variant.chromosome}:"
                f"{parent2_variant.position}. "
                f"Potential compound-heterozygous candidate; "
                f"phase and clinical evidence require further evaluation."
            )

            compound_candidates.append(description)

    # ---------------------------------------------------------
    # Build final assessment
    # ---------------------------------------------------------

    return OffspringRiskAssessmentResponse(
        status="completed",
        risks=offspring_risks,
        shared_risk_count=len(offspring_risks),
        uncertain_variant_count=0,
        compound_heterozygous_candidates=compound_candidates,
        consanguinity_context=consanguinity_context,
        limitations=limitations,
    )