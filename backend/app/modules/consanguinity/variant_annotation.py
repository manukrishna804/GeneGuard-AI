from __future__ import annotations

from typing import List

from .annotation import annotate_variant
from .annotation_provider import AnnotationProvider
from .schemas import GeneticVariant


def annotate_variants(
    variants: List[GeneticVariant],
    provider: AnnotationProvider,
) -> List[GeneticVariant]:
    """
    Annotate a list of variants using the supplied annotation provider.

    Variants for which the provider has no annotation are kept unchanged.
    """

    annotated_variants: List[GeneticVariant] = []

    for variant in variants:
        annotated_variant = annotate_variant(
            variant,
            provider,
        )

        annotated_variants.append(
            annotated_variant
        )

    return annotated_variants