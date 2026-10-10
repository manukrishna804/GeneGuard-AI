from __future__ import annotations

from typing import List

from .schemas import GeneticVariant


def find_same_gene_different_variants(
    parent1_variants: List[GeneticVariant],
    parent2_variants: List[GeneticVariant],
) -> List[tuple[GeneticVariant, GeneticVariant]]:
    """
    Find candidate same-gene/different-variant pairs.

    A candidate is identified when:
      - both variants have the same known gene
      - the variants are different genomic variants

    This function only identifies candidates for possible
    compound heterozygosity. It does not establish phase
    or calculate offspring risk.
    """

    candidates: List[
        tuple[GeneticVariant, GeneticVariant]
    ] = []

    for parent1_variant in parent1_variants:

        if (
            not parent1_variant.gene
            or parent1_variant.gene == "UNKNOWN"
        ):
            continue

        for parent2_variant in parent2_variants:

            if (
                not parent2_variant.gene
                or parent2_variant.gene == "UNKNOWN"
            ):
                continue

            # Same gene
            if parent1_variant.gene != parent2_variant.gene:
                continue

            # Same exact variant is handled separately
            same_variant = (
                parent1_variant.chromosome
                == parent2_variant.chromosome
                and parent1_variant.position
                == parent2_variant.position
                and parent1_variant.reference
                == parent2_variant.reference
                and parent1_variant.alternate
                == parent2_variant.alternate
            )

            if same_variant:
                continue

            candidates.append(
                (
                    parent1_variant,
                    parent2_variant,
                )
            )

    return candidates