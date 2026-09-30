from typing import Any, Dict, List, Set


# Pharmacogenes currently supported by Module 5.
#
# This list follows the genes identified in the Module 5
# specification. We will expand the reference data later.
SUPPORTED_PHARMACOGENES: Set[str] = {
    "CYP2D6",
    "CYP2C19",
    "CYP2C9",
    "CYP3A5",
    "TPMT",
    "NUDT15",
    "DPYD",
    "SLCO1B1",
    "VKORC1",
    "HLA-B",
    "HLA-A",
    "UGT1A1",
    "G6PD",
}


def normalize_gene_name(gene: str | None) -> str | None:
    """
    Normalize a gene name before comparing it with the
    supported pharmacogene list.
    """

    if not gene:
        return None

    return gene.strip().upper()


def filter_pharmacogenes(
    variants: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Filter the complete variant list and keep only variants
    belonging to supported pharmacogenes.

    Input:
        List of variants from Module 1.

    Output:
        Dictionary grouped by pharmacogene.

    Example:

        {
            "CYP2C19": [
                {
                    "rsid": "rs4244285",
                    "genotype": "A/G",
                    ...
                }
            ]
        }
    """

    filtered: Dict[str, List[Dict[str, Any]]] = {}

    for variant in variants:
        gene = normalize_gene_name(
            variant.get("gene")
        )

        if not gene:
            continue

        if gene not in SUPPORTED_PHARMACOGENES:
            continue

        if gene not in filtered:
            filtered[gene] = []

        filtered[gene].append(variant)

    return filtered


def get_supported_pharmacogenes() -> List[str]:
    """
    Return the list of pharmacogenes currently supported
    by Module 5.
    """

    return sorted(SUPPORTED_PHARMACOGENES)