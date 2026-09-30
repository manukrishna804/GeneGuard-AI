from typing import Any, Dict, List


# ============================================================
# INITIAL GENE-DRUG PAIRS
# ============================================================
#
# This is the initial development dataset.
#
# Later we will move this into:
#
# data/gene_drug_pairs.json
#
# and expand it using the project's intended PGx sources.
# ============================================================

GENE_DRUG_PAIRS: Dict[str, Dict[str, Dict[str, Any]]] = {

    "CYP2C19": {

        "clopidogrel": {
            "display_name": "Clopidogrel",
            "guideline_id": "CPIC-CYP2C19-Clopidogrel",
        },

    },

    "CYP2D6": {

        "codeine": {
            "display_name": "Codeine",
            "guideline_id": "CPIC-CYP2D6-Codeine",
        },

        "tramadol": {
            "display_name": "Tramadol",
            "guideline_id": "CPIC-CYP2D6-Tramadol",
        },

    },

    "TPMT": {

        "azathioprine": {
            "display_name": "Azathioprine",
            "guideline_id": "CPIC-TPMT-Azathioprine",
        },

        "mercaptopurine": {
            "display_name": "Mercaptopurine",
            "guideline_id": "CPIC-TPMT-Mercaptopurine",
        },

    },

    "NUDT15": {

        "azathioprine": {
            "display_name": "Azathioprine",
            "guideline_id": "CPIC-NUDT15-Azathioprine",
        },

        "mercaptopurine": {
            "display_name": "Mercaptopurine",
            "guideline_id": "CPIC-NUDT15-Mercaptopurine",
        },

    },

    "DPYD": {

        "fluorouracil": {
            "display_name": "Fluorouracil",
            "guideline_id": "CPIC-DPYD-Fluorouracil",
        },

        "capecitabine": {
            "display_name": "Capecitabine",
            "guideline_id": "CPIC-DPYD-Capecitabine",
        },

    },

    "SLCO1B1": {

        "simvastatin": {
            "display_name": "Simvastatin",
            "guideline_id": "CPIC-SLCO1B1-Simvastatin",
        },

    },

    "CYP2C9": {

        "warfarin": {
            "display_name": "Warfarin",
            "guideline_id": "CPIC-CYP2C9-Warfarin",
        },

    },

}


def normalize_drug_name(drug: str) -> str:
    """
    Normalize a medication name for matching.

    Example:

        " Clopidogrel "
            ↓
        "clopidogrel"
    """

    return drug.strip().lower()


def get_gene_drug_pair(
    gene: str,
    drug: str,
) -> Dict[str, Any] | None:
    """
    Find a gene-drug pair in the reference table.

    Returns None if no established pair is currently
    available in our reference data.
    """

    normalized_gene = gene.strip().upper()
    normalized_drug = normalize_drug_name(drug)

    gene_pairs = GENE_DRUG_PAIRS.get(
        normalized_gene,
        {},
    )

    return gene_pairs.get(normalized_drug)


def match_drugs_to_genes(
    medications: List[Dict[str, Any]],
    phenotype_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Match patient medications against the patient's
    pharmacogenomic genes.

    Parameters
    ----------
    medications:
        Patient medication list.

    phenotype_results:
        Results produced by phenotype_mapper.py.

    Returns
    -------
    List of matched gene-drug combinations.
    """

    matches: List[Dict[str, Any]] = []

    for medication in medications:

        drug_name = medication.get("name")

        if not drug_name:
            continue

        normalized_drug = normalize_drug_name(
            drug_name
        )

        for phenotype in phenotype_results:

            gene = phenotype.get("gene")

            if not gene:
                continue

            pair = get_gene_drug_pair(
                gene=gene,
                drug=normalized_drug,
            )

            if not pair:
                continue

            matches.append(
                {
                    "drug": pair["display_name"],
                    "gene": gene,
                    "pair_found": True,
                    "cpic_guideline_id": pair[
                        "guideline_id"
                    ],
                    "diplotype": phenotype.get(
                        "diplotype"
                    ),
                    "phenotype": phenotype.get(
                        "phenotype"
                    ),
                    "activity_score": phenotype.get(
                        "activity_score"
                    ),
                }
            )

    return matches


def get_supported_gene_drug_pairs() -> List[Dict[str, str]]:
    """
    Return all currently supported gene-drug pairs.

    Useful later for:
        - API documentation
        - frontend dropdowns
        - testing
        - debugging
    """

    pairs: List[Dict[str, str]] = []

    for gene, drugs in GENE_DRUG_PAIRS.items():

        for drug_key, details in drugs.items():

            pairs.append(
                {
                    "gene": gene,
                    "drug": details["display_name"],
                    "guideline_id": details[
                        "guideline_id"
                    ],
                }
            )

    return pairs