from typing import Any, Dict, List


def aggregate_evidence(
    gene_drug_pair: Dict[str, Any],
    cpic: Dict[str, Any] | None = None,
    pharmgkb: Dict[str, Any] | None = None,
    pharmvar: List[Dict[str, Any]] | None = None,
    drugbank: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Combine evidence from all Module 5 evidence sources
    into one normalized evidence package.

    Parameters
    ----------
    gene_drug_pair:
        Gene-drug matching result from drug_matcher.py.

    cpic:
        CPIC guideline result.

    pharmgkb:
        PharmGKB / ClinPGx evidence.

    pharmvar:
        PharmVar allele definitions.

    drugbank:
        DrugBank pharmacology/interaction context.

    Returns
    -------
    Unified evidence dictionary.
    """

    return {
        "gene_drug_pair": gene_drug_pair,

        "cpic": cpic or {
            "available": False,
            "source": "CPIC",
        },

        "pharmgkb": pharmgkb or {
            "available": False,
            "source": "PharmGKB",
        },

        "pharmvar": pharmvar or [],

        "drugbank": drugbank or {
            "available": False,
            "source": "DrugBank",
        },
    }


def aggregate_multiple_evidence(
    matched_pairs: List[Dict[str, Any]],
    cpic_results: Dict[str, Dict[str, Any]] | None = None,
    pharmgkb_results: Dict[str, Dict[str, Any]] | None = None,
    pharmvar_results: Dict[str, List[Dict[str, Any]]] | None = None,
    drugbank_results: Dict[str, Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    """
    Aggregate evidence for multiple gene-drug pairs.

    The dictionaries use a simple key:

        GENE:DRUG

    Example:

        CYP2C19:Clopidogrel
    """

    cpic_results = cpic_results or {}
    pharmgkb_results = pharmgkb_results or {}
    pharmvar_results = pharmvar_results or {}
    drugbank_results = drugbank_results or {}

    aggregated: List[Dict[str, Any]] = []

    for pair in matched_pairs:

        gene = pair.get("gene")
        drug = pair.get("drug")

        if not gene or not drug:
            continue

        key = f"{gene}:{drug}"

        evidence = aggregate_evidence(
            gene_drug_pair=pair,

            cpic=cpic_results.get(key),

            pharmgkb=pharmgkb_results.get(key),

            pharmvar=pharmvar_results.get(key),

            drugbank=drugbank_results.get(key),
        )

        aggregated.append(evidence)

    return aggregated