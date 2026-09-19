from __future__ import annotations

from .assessment_builder import build_assessment_response
from .clinvar_provider import ClinVarProvider
from .risk_calculator import calculate_shared_variant_risks
from .risk_filter import filter_risk_relevant_variants
from .schemas import (
    ConsanguinityInfo,
    OffspringRiskAssessmentResponse,
)
from .variant_annotation import annotate_variants
from .vcf_parser import parse_vcf


def assess_offspring_risk_from_vcfs(
    parent1_vcf: str,
    parent2_vcf: str,
    consanguinity: ConsanguinityInfo | None = None,
) -> OffspringRiskAssessmentResponse:
    """
    Run the complete Module 4 offspring-risk workflow
    using two parental VCF files.
    """

    # ---------------------------------------------------------
    # 1. Create annotation provider
    # ---------------------------------------------------------

    provider = ClinVarProvider()

    # ---------------------------------------------------------
    # 2. Parse parental VCF files
    # ---------------------------------------------------------

    parent1_variants = parse_vcf(parent1_vcf)
    parent2_variants = parse_vcf(parent2_vcf)

    # ---------------------------------------------------------
    # 3. Annotate variants
    # ---------------------------------------------------------

    parent1_variants = annotate_variants(
        parent1_variants,
        provider,
    )

    parent2_variants = annotate_variants(
        parent2_variants,
        provider,
    )

    # ---------------------------------------------------------
    # 4. Keep only risk-relevant variants
    # ---------------------------------------------------------

    parent1_variants = filter_risk_relevant_variants(
        parent1_variants
    )

    parent2_variants = filter_risk_relevant_variants(
        parent2_variants
    )

    # ---------------------------------------------------------
    # 5. Calculate shared-variant offspring risks
    # ---------------------------------------------------------

    risks = calculate_shared_variant_risks(
        parent1_variants,
        parent2_variants,
    )

    # ---------------------------------------------------------
    # 6. Build overall assessment
    # ---------------------------------------------------------

    return build_assessment_response(
        risks,
        consanguinity,
    )