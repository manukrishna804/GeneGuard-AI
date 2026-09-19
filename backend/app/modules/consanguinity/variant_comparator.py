from __future__ import annotations

from typing import List, Tuple

from .schemas import GeneticVariant


def variant_key(
    variant: GeneticVariant,
) -> Tuple[str, int | None, str | None, str | None]:
    """
    Create a normalized key used to compare variants between parents.
    """
    return (
        variant.chromosome or "",
        variant.position,
        variant.reference,
        variant.alternate,
    )


def find_shared_variants(
    parent1_variants: List[GeneticVariant],
    parent2_variants: List[GeneticVariant],
) -> List[GeneticVariant]:
    """
    Find variants that are present in both parents.
    """

    parent2_keys = {
        variant_key(variant)
        for variant in parent2_variants
    }

    return [
        variant
        for variant in parent1_variants
        if variant_key(variant) in parent2_keys
    ]


def compare_parent_variants(
    parent1_variants: List[GeneticVariant],
    parent2_variants: List[GeneticVariant],
) -> dict:
    """
    Compare the variants carried by two parents.
    """

    parent1_keys = {
        variant_key(variant)
        for variant in parent1_variants
    }

    parent2_keys = {
        variant_key(variant)
        for variant in parent2_variants
    }

    shared_keys = parent1_keys & parent2_keys
    parent1_only_keys = parent1_keys - parent2_keys
    parent2_only_keys = parent2_keys - parent1_keys

    shared_variants = [
        variant
        for variant in parent1_variants
        if variant_key(variant) in shared_keys
    ]

    parent1_only = [
        variant
        for variant in parent1_variants
        if variant_key(variant) in parent1_only_keys
    ]

    parent2_only = [
        variant
        for variant in parent2_variants
        if variant_key(variant) in parent2_only_keys
    ]

    return {
        "shared_variants": shared_variants,
        "parent1_only": parent1_only,
        "parent2_only": parent2_only,
    }