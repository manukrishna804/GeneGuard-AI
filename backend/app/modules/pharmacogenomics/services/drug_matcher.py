import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from app.modules.pharmacogenomics.config import pgx_settings


def load_gene_drug_pairs() -> List[Dict[str, Any]]:
    pairs_file = pgx_settings.DATA_DIR / "gene_drug_pairs.json"
    if pairs_file.exists():
        with open(pairs_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


GENE_DRUG_PAIRS = load_gene_drug_pairs()


def normalize_drug_name(drug_query: str) -> Optional[Dict[str, Any]]:
    """
    Match user-supplied drug name (generic or brand name) against known gene-drug database.
    """
    clean_query = drug_query.strip().lower()
    
    for pair in GENE_DRUG_PAIRS:
        # Match generic name
        if clean_query == pair["drug_name"].lower():
            return pair
            
        # Match brand names
        brand_matches = [b.lower() for b in pair.get("brand_names", [])]
        if clean_query in brand_matches or any(clean_query in b or b in clean_query for b in brand_matches):
            return pair
            
    # Fuzzy substring match
    for pair in GENE_DRUG_PAIRS:
        if clean_query in pair["drug_name"].lower() or pair["drug_name"].lower() in clean_query:
            return pair
            
    return None


def match_medications_to_genes(medication_list: List[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Stage 5: Cross patient's medication list against CPIC/PharmGKB gene-drug pairs.
    Returns:
      (matched_pairs, unmatched_drugs)
    """
    matched_pairs: List[Dict[str, Any]] = []
    unmatched_drugs: List[str] = []
    seen_drugs: Set[str] = set()

    for med in medication_list:
        med_str = str(med).strip()
        if not med_str:
            continue
            
        match = normalize_drug_name(med_str)
        if match:
            canonical_name = match["drug_name"]
            if canonical_name not in seen_drugs:
                seen_drugs.add(canonical_name)
                matched_pairs.append({
                    "user_query": med_str,
                    "drug_name": canonical_name,
                    "primary_gene": match["primary_gene"],
                    "secondary_genes": match.get("secondary_genes", []),
                    "therapeutic_area": match.get("therapeutic_area", "General"),
                    "cpic_level": match.get("cpic_level", "A"),
                    "pharmgkb_level": match.get("pharmgkb_level", "1A"),
                    "fda_label_status": match.get("fda_label_status", "Actionable PGx")
                })
        else:
            unmatched_drugs.append(med_str)

    return matched_pairs, unmatched_drugs
