from typing import Any, Dict, List, Tuple


def evaluate_evidence_conflict(evidence_record: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]], float]:
    """
    Stage 8: Evaluate evidence consistency and detect conflicts or uncertainty flags.
    Returns:
      (has_conflict, conflict_list, confidence_score)
    """
    conflicts: List[Dict[str, Any]] = []
    drug = evidence_record["gene_drug_pair"]["drug"]
    gene = evidence_record["gene_drug_pair"]["gene"]
    genomic = evidence_record["genomic_profile"]
    guidelines = evidence_record["guideline_evidence"]

    base_confidence = 98.0

    # 1. Check for Indeterminate / Ambiguous phenotype
    if "Indeterminate" in genomic.get("phenotype", ""):
        conflicts.append({
            "type": "indeterminate_phenotype",
            "drug": drug,
            "gene": gene,
            "severity": "HIGH",
            "message": f"Uncertain diplotype or activity score mapping for {gene} ({genomic.get('diplotype')}).",
            "action": "Manual review by Clinical Pharmacist / Molecular Geneticist required."
        })
        base_confidence -= 20.0

    # 2. Check for Lower PharmGKB evidence level on CPIC Level A drug
    pharmgkb_lvl = str(guidelines.get("pharmgkb_level", "1A"))
    if pharmgkb_lvl in ["3", "4"]:
        conflicts.append({
            "type": "evidence_level_divergence",
            "drug": drug,
            "gene": gene,
            "severity": "MEDIUM",
            "message": f"PharmGKB evidence level ({pharmgkb_lvl}) is lower than primary guideline consensus.",
            "action": "Cross-reference clinical literature before dose modification."
        })
        base_confidence -= 8.0

    # 3. High toxicity / high-risk drugs require pharmacist sign-off
    if guidelines.get("requires_clinical_review"):
        if "Poor" in genomic.get("phenotype", "") or "High Risk" in genomic.get("phenotype", ""):
            conflicts.append({
                "type": "high_risk_clinical_gate",
                "drug": drug,
                "gene": gene,
                "severity": "CRITICAL",
                "message": f"Actionable critical risk: {genomic.get('phenotype')} with {drug}. High risk of adverse reaction or treatment failure.",
                "action": f"Route to {guidelines.get('specialist_routing', 'Clinical Pharmacist')} for prescription adjustment approval."
            })
            base_confidence -= 2.0  # slight confidence adjustment for flagged review gate

    has_conflict = len(conflicts) > 0
    final_confidence = max(60.0, min(100.0, base_confidence))

    return has_conflict, conflicts, final_confidence
