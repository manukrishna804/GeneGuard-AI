from __future__ import annotations

from .annotation_provider import AnnotationProvider
from .schemas import GeneticVariant


def annotate_variant(
    variant: GeneticVariant,
    provider: AnnotationProvider | None = None,
) -> GeneticVariant:
    """
    Annotate a variant using the supplied annotation provider.

    If no provider is supplied, the original variant is returned.
    """

    if provider is None:
        return variant

    annotated_variant = provider.annotate(variant)

    if annotated_variant is None:
        return variant

    return annotated_variant