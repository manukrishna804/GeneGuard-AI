from typing import Any, Dict, List


def aggregate_gene_drug_evidence(
    pair_info: Dict[str, Any],
    diplotype_info: Dict[str, Any],
    guideline_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Stage 7: Aggregate all multi-source evidence into a master structured evidence document per gene-drug pair.
    """
    drug_name = pair_info["drug_name"]
    gene = pair_info["primary_gene"]
    
    aggregated = {
        "gene_drug_pair": {
            "drug": drug_name,
            "gene": gene,
            "secondary_genes": pair_info.get("secondary_genes", []),
            "therapeutic_area": pair_info.get("therapeutic_area", "General")
        },
        "genomic_profile": {
            "gene": gene,
            "diplotype": diplotype_info.get("diplotype", "*1/*1"),
            "allele1": diplotype_info.get("allele1", "*1"),
            "allele2": diplotype_info.get("allele2", "*1"),
            "activity_score": diplotype_info.get("activity_score"),
            "phenotype": diplotype_info.get("phenotype", "Normal Metabolizer"),
            "phenotype_code": diplotype_info.get("phenotype_code", "NM"),
            "evidence_alleles": diplotype_info.get("evidence_alleles", [])
        },
        "guideline_evidence": {
            "cpic_recommendation": guideline_info.get("recommendation"),
            "clinical_implication": guideline_info.get("clinical_implication"),
            "actionability": guideline_info.get("actionability"),
            "cpic_evidence_level": guideline_info.get("evidence_level"),
            "pharmgkb_level": guideline_info.get("pharmgkb_level"),
            "guideline_source": guideline_info.get("source"),
            "fda_labeling": guideline_info.get("local_fda"),
            "specialist_routing": guideline_info.get("specialist", "Clinical Pharmacist"),
            "requires_clinical_review": guideline_info.get("requires_review", False)
        }
    }
    
    return aggregated
