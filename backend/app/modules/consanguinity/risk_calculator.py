from __future__ import annotations

from typing import List

from .genetics_engine import InheritanceMode, punnett_square
from .inheritance import get_inheritance_mode
from .schemas import GeneticVariant, VariantRiskResult
from .status_mapper import zygosity_to_ar_status
from .variant_comparator import variant_key
from .risk_interpreter import interpret_variant_risk


def calculate_shared_variant_risks(
    parent1_variants: List[GeneticVariant],
    parent2_variants: List[GeneticVariant],
    mode: InheritanceMode | None = None,
) -> List[VariantRiskResult]:
    """
    Calculate preliminary offspring risk distributions for variants
    shared by both parents.

    If an inheritance mode is explicitly supplied, it is used for
    all variants.

    Otherwise, the inheritance mode is determined from the condition
    associated with each variant.

    Currently, the risk engine supports the inheritance modes
    implemented by genetics_engine.py.
    """

    parent2_by_key = {
        variant_key(variant): variant
        for variant in parent2_variants
    }

    risks: List[VariantRiskResult] = []

    for parent1_variant in parent1_variants:

        key = variant_key(parent1_variant)

        # ---------------------------------------------------------
        # Check whether the same variant is present in parent 2
        # ---------------------------------------------------------

        if key not in parent2_by_key:
            continue

        parent2_variant = parent2_by_key[key]

        # ---------------------------------------------------------
        # Determine inheritance mode
        # ---------------------------------------------------------

        if mode is not None:
            calculation_mode = mode
        else:
            calculation_mode = get_inheritance_mode(
                parent1_variant.condition
            )

        # ---------------------------------------------------------
        # Do not calculate unsupported/unknown inheritance
        # ---------------------------------------------------------

        if calculation_mode == InheritanceMode.UNKNOWN:
            continue

        # ---------------------------------------------------------
        # Convert zygosity into simplified parental status
        # ---------------------------------------------------------

        parent1_status = zygosity_to_ar_status(
            parent1_variant.zygosity
        )

        parent2_status = zygosity_to_ar_status(
            parent2_variant.zygosity
        )

        # ---------------------------------------------------------
        # Calculate offspring probabilities
        # ---------------------------------------------------------

        probability = punnett_square(
            parent1_status,
            parent2_status,
            calculation_mode,
        )

        # ---------------------------------------------------------
        # Create enriched risk result
        # ---------------------------------------------------------

        risk_result = VariantRiskResult(
            chromosome=parent1_variant.chromosome,
            position=parent1_variant.position,
            reference=parent1_variant.reference,
            alternate=parent1_variant.alternate,

            # Variant annotation
            gene=parent1_variant.gene,
            variant_name=parent1_variant.variant_name,
            condition=parent1_variant.condition,
            inheritance=(
                calculation_mode.value
                if hasattr(calculation_mode, "value")
                else str(calculation_mode)
            ),
            classification=parent1_variant.classification,
            evidence_sources=parent1_variant.evidence_sources,

            # Parent status
            parent1_status=parent1_status.value,
            parent2_status=parent2_status.value,

            # Offspring probability
            affected_probability=probability["affected"],
            carrier_probability=probability["carrier"],
            unaffected_probability=probability["unaffected"],
        )

        risk_result.explanation = interpret_variant_risk(
            risk_result
        )

        risks.append(risk_result)

    return risks