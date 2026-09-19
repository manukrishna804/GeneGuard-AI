from __future__ import annotations

from typing import List

from .schemas import GeneticVariant, VariantClassification


RISK_RELEVANT_CLASSIFICATIONS = {
    VariantClassification.PATHOGENIC,
    VariantClassification.LIKELY_PATHOGENIC,
}


def filter_risk_relevant_variants(
    variants: List[GeneticVariant],
) -> List[GeneticVariant]:
    """
    Return variants with classifications suitable for
    preliminary Mendelian risk calculation.

    Only Pathogenic and Likely Pathogenic variants are included.
    """

    return [
        variant
        for variant in variants
        if variant.classification
        in RISK_RELEVANT_CLASSIFICATIONS
    ]