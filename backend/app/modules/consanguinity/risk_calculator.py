from __future__ import annotations

from typing import Dict, List

from .genetics_engine import InheritanceMode, punnett_square
from .schemas import GeneticVariant, VariantRiskResult
from .status_mapper import zygosity_to_ar_status
from .variant_comparator import variant_key


def calculate_shared_variant_risks(
    parent1_variants: List[GeneticVariant],
    parent2_variants: List[GeneticVariant],
    mode: InheritanceMode = InheritanceMode.AUTOSOMAL_RECESSIVE,
) -> List[VariantRiskResult]:
    """
    Calculate preliminary offspring risk distributions for variants
    shared by both parents.

    This currently supports autosomal-recessive inheritance only.
    """

    parent2_by_key = {
        variant_key(variant): variant
        for variant in parent2_variants
    }

    risks: List[VariantRiskResult] = []

    for parent1_variant in parent1_variants:

        key = variant_key(parent1_variant)

        if key not in parent2_by_key:
            continue

        parent2_variant = parent2_by_key[key]

        parent1_status = zygosity_to_ar_status(
            parent1_variant.zygosity
        )

        parent2_status = zygosity_to_ar_status(
            parent2_variant.zygosity
        )

        probability = punnett_square(
            parent1_status,
            parent2_status,
            mode,
        )

        risks.append(
            VariantRiskResult(
                chromosome=parent1_variant.chromosome,
                position=parent1_variant.position,
                reference=parent1_variant.reference,
                alternate=parent1_variant.alternate,
                parent1_status=parent1_status.value,
                parent2_status=parent2_status.value,
                affected_probability=probability["affected"],
                carrier_probability=probability["carrier"],
                unaffected_probability=probability["unaffected"],
            )
        )

    return risks