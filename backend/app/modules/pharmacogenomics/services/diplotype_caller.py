from typing import Any, Dict, List, Optional


def normalize_star_allele(allele: str) -> str:
    """
    Normalize a star allele.

    Examples:
        "1"   -> "*1"
        "*1"  -> "*1"
        " *2 " -> "*2"
    """

    allele = allele.strip()

    if not allele.startswith("*"):
        allele = f"*{allele}"

    return allele


def build_diplotype(
    gene: str,
    star_alleles: List[str],
) -> Optional[str]:
    """
    Build a diplotype from two star alleles.

    Example:
        ["*2", "*2"] -> "*2/*2"

    A diplotype requires two alleles.
    """

    if len(star_alleles) < 2:
        return None

    normalized = [
        normalize_star_allele(allele)
        for allele in star_alleles[:2]
    ]

    return f"{normalized[0]}/{normalized[1]}"


def call_diplotype(
    gene: str,
    variants: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Determine the available star-allele information for a gene
    and construct a diplotype when two star alleles are available.

    IMPORTANT:
    This is the initial implementation.

    It does NOT attempt to perform full clinical-grade
    star-allele calling from raw VCF data.

    Later this service can be connected to:
        - Aldy
        - Stargazer
        - Cyrius

    for genes with complex structural variation, especially CYP2D6.
    """

    star_alleles: List[str] = []

    for variant in variants:

        # Preferred field if an upstream service has already
        # determined the star allele.
        star_allele = variant.get("star_allele")

        if star_allele:
            star_alleles.append(
                normalize_star_allele(star_allele)
            )

    # Keep duplicate alleles because they can represent
# a homozygous diplotype such as *2/*2.
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
    """
    Call diplotypes for all filtered pharmacogenes.

    Input:

        {
            "CYP2C19": [...],
            "CYP2D6": [...],
            "TPMT": [...]
        }

    Output:

        [
            {
                "gene": "CYP2C19",
                "star_alleles": ["*2", "*2"],
                "diplotype": "*2/*2",
                "status": "complete"
            }
        ]
    """

    results: List[Dict[str, Any]] = []

    for gene, variants in pharmacogene_variants.items():

        result = call_diplotype(
            gene=gene,
            variants=variants,
        )

        results.append(result)

    return results