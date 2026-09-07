import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from app.modules.pharmacogenomics.config import pgx_settings


def load_phenotype_rules() -> Dict[str, Any]:
    rules_file = pgx_settings.DATA_DIR / "phenotype_rules.json"
    if rules_file.exists():
        with open(rules_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_allele_definitions() -> Dict[str, Any]:
    allele_file = pgx_settings.DATA_DIR / "allele_definitions.json"
    if allele_file.exists():
        with open(allele_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


PHENOTYPE_RULES = load_phenotype_rules()
ALLELE_DEFS = load_allele_definitions()


def calculate_activity_score(gene: str, allele1: str, allele2: str) -> Optional[float]:
    """
    Calculate CPIC activity score for a given gene and two alleles.
    """
    gene_def = ALLELE_DEFS.get(gene, {})
    alleles_dict = gene_def.get("alleles", {})

    val1 = alleles_dict.get(allele1, {}).get("activity_value")
    val2 = alleles_dict.get(allele2, {}).get("activity_value")

    if val1 is not None and val2 is not None:
        return round(float(val1) + float(val2), 2)

    return None


def map_diplotype_to_phenotype(gene: str, diplotype_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 4: Map diplotype to metabolizer phenotype using CPIC function tables.
    """
    # HLA Direct Allele handling
    if gene.startswith("HLA"):
        if diplotype_info.get("is_risk_positive"):
            allele = diplotype_info.get("allele1")
            if "57:01" in str(allele):
                phenotype = "Abacavir Hypersensitivity High Risk (Positive)"
            elif "58:01" in str(allele):
                phenotype = "Allopurinol Severe Cutaneous Reaction High Risk (Positive)"
            elif "15:02" in str(allele):
                phenotype = "Carbamazepine SJS/TEN High Risk (Positive)"
            elif "31:01" in str(allele):
                phenotype = "Carbamazepine Hypersensitivity High Risk (Positive)"
            else:
                phenotype = "Risk Allele Positive"
            code = "POS"
        else:
            phenotype = "Low Risk / Negative"
            code = "NEG"

        return {
            **diplotype_info,
            "activity_score": None,
            "phenotype": phenotype,
            "phenotype_code": code,
            "source": "CPIC / ClinPGx HLA Guidelines"
        }

    # VKORC1 handling
    if gene == "VKORC1":
        dip = diplotype_info.get("diplotype", "")
        if "A/A" in dip:
            phenotype = "High Sensitivity (Low Dose Required)"
            code = "High Sensitivity"
            score = 0.0
        elif "G/A" in dip:
            phenotype = "Intermediate Sensitivity (Moderate Dose)"
            code = "Intermediate Sensitivity"
            score = 1.0
        else:
            phenotype = "Normal Sensitivity (Standard Dose)"
            code = "Normal Sensitivity"
            score = 2.0

        return {
            **diplotype_info,
            "activity_score": score,
            "phenotype": phenotype,
            "phenotype_code": code,
            "source": "CPIC Warfarin Guidelines"
        }

    # Activity Score based mapping
    a1 = diplotype_info.get("allele1", "*1")
    a2 = diplotype_info.get("allele2", "*1")
    activity_score = calculate_activity_score(gene, a1, a2)

    thresholds = PHENOTYPE_RULES.get("activity_score_thresholds", {}).get(gene, [])
    
    phenotype = "Normal Metabolizer"
    phenotype_code = "NM"

    if activity_score is not None:
        for t in thresholds:
            if t["min_score"] <= activity_score <= t["max_score"]:
                phenotype = t["phenotype"]
                phenotype_code = t["code"]
                break
    else:
        # Fallback if activity score could not be computed
        if a1 == "*1" and a2 == "*1":
            phenotype = "Normal Metabolizer"
            phenotype_code = "NM"
            activity_score = 2.0
        else:
            phenotype = "Indeterminate Metabolizer"
            phenotype_code = "IND"

    return {
        **diplotype_info,
        "activity_score": activity_score,
        "phenotype": phenotype,
        "phenotype_code": phenotype_code,
        "source": "CPIC Activity Score & Phenotype Consensus Tables"
    }


def map_all_diplotypes_to_phenotypes(diplotypes: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Process all diplotype calls and attach CPIC phenotypes.
    """
    results = {}
    for gene, dip_info in diplotypes.items():
        results[gene] = map_diplotype_to_phenotype(gene, dip_info)
    return results
