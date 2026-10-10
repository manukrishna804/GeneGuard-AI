
from typing import Any, Dict, List, Optional


def normalize_star_allele(allele: str) -> str:
    """Normalize a star-allele label."""
    allele = allele.strip()

    if not allele.startswith("*"):
        allele = f"*{allele}"

    return allele


def build_diplotype(
    gene: str,
    star_alleles: List[str],
) -> Optional[str]:
    """Build a diplotype only when two alleles are available."""
    if len(star_alleles) != 2:
        return None

    normalized = [
        normalize_star_allele(allele)
        for allele in star_alleles
    ]

    return f"{normalized[0]}/{normalized[1]}"


def call_diplotype(
    gene: str,
    variants: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Use star alleles supplied by an upstream validated caller.

    This function does not infer star alleles from gene annotations
    or raw variants.
    """
    star_alleles: List[str] = []

    for variant in variants:
        star_allele = variant.get("star_allele")

        if star_allele:
            star_alleles.append(
                normalize_star_allele(str(star_allele))
            )

    diplotype = build_diplotype(
        gene=gene,
        star_alleles=star_alleles,
    )

    return {
        "gene": gene,
        "star_alleles": star_alleles,
        "diplotype": diplotype,
        "status": (
            "complete"
            if diplotype
            else "insufficient_data"
        ),
    }


def call_diplotypes(
    pharmacogene_variants: Dict[str, List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Call diplotypes for all filtered pharmacogenes."""
    results: List[Dict[str, Any]] = []

    for gene, variants in pharmacogene_variants.items():
        results.append(
            call_diplotype(
                gene=gene,
                variants=variants,
            )
        )

    return results
