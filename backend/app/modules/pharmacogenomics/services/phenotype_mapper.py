from typing import Any, Dict, List, Optional


# ============================================================
# PHENOTYPE RULES
# ============================================================
#
# Initial rule set for development/testing.
#
# These rules will later be moved into:
#
# data/phenotype_rules.json
#
# and expanded using the appropriate CPIC gene-specific
# function/activity-score tables.
# ============================================================


PHENOTYPE_RULES: Dict[str, Dict[str, Dict[str, Any]]] = {

    "CYP2C19": {

        "*1/*1": {
            "activity_score": 2.0,
            "phenotype": "Normal Metabolizer",
        },

        "*1/*2": {
            "activity_score": 1.0,
            "phenotype": "Intermediate Metabolizer",
        },

        "*2/*1": {
            "activity_score": 1.0,
            "phenotype": "Intermediate Metabolizer",
        },

        "*2/*2": {
            "activity_score": 0.0,
            "phenotype": "Poor Metabolizer",
        },

        "*1/*17": {
            "activity_score": 2.0,
            "phenotype": "Rapid Metabolizer",
        },

        "*17/*1": {
            "activity_score": 2.0,
            "phenotype": "Rapid Metabolizer",
        },

        "*17/*17": {
            "activity_score": 2.0,
            "phenotype": "Ultrarapid Metabolizer",
        },
    }
}


def normalize_diplotype(diplotype: str) -> str:
    """
    Normalize a diplotype so that:

        *2/*1

    and

        *1/*2

    are treated consistently.

    The alleles are sorted alphabetically by their numeric
    star-allele value.
    """

    if not diplotype:
        return diplotype

    parts = [
        part.strip()
        for part in diplotype.split("/")
        if part.strip()
    ]

    if len(parts) != 2:
        return diplotype

    parts = sorted(
        parts,
        key=lambda allele: allele.replace("*", "")
    )

    return f"{parts[0]}/{parts[1]}"


def map_diplotype_to_phenotype(
    gene: str,
    diplotype: Optional[str],
) -> Dict[str, Any]:
    """
    Convert a diplotype into an activity score and
    metabolizer phenotype.

    Returns an explicit 'unknown' result when a diplotype
    is not available in the current rule set.
    """

    if not diplotype:
        return {
            "gene": gene,
            "diplotype": None,
            "activity_score": None,
            "phenotype": None,
            "status": "missing_diplotype",
        }

    normalized_diplotype = normalize_diplotype(
        diplotype
    )

    gene_rules = PHENOTYPE_RULES.get(gene, {})

    rule = gene_rules.get(normalized_diplotype)

    if not rule:
        return {
            "gene": gene,
            "diplotype": normalized_diplotype,
            "activity_score": None,
            "phenotype": None,
            "status": "unknown_diplotype",
        }

    return {
        "gene": gene,
        "diplotype": normalized_diplotype,
        "activity_score": rule["activity_score"],
        "phenotype": rule["phenotype"],
        "status": "mapped",
    }


def map_phenotypes(
    diplotype_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Map all available diplotype results to phenotypes.

    Input:

        [
            {
                "gene": "CYP2C19",
                "diplotype": "*2/*2"
            }
        ]

    Output:

        [
            {
                "gene": "CYP2C19",
                "diplotype": "*2/*2",
                "activity_score": 0.0,
                "phenotype": "Poor Metabolizer",
                "status": "mapped"
            }
        ]
    """

    results: List[Dict[str, Any]] = []

    for result in diplotype_results:

        gene = result.get("gene")
        diplotype = result.get("diplotype")

        if not gene:
            continue

        phenotype_result = map_diplotype_to_phenotype(
            gene=gene,
            diplotype=diplotype,
        )

        results.append(phenotype_result)

    return results