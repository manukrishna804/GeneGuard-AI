
from typing import Any, Dict, List, Optional


# ============================================================
# INITIAL RECOMMENDATION RULES
# ============================================================
#
# These are development fallback rules for the first working
# pipeline.
#
# When an applicable recommendation is successfully retrieved
# from CPIC/ClinPGx, the retrieved recommendation takes priority.
#
# These local rules are not a substitute for validated clinical
# guidelines and must not be used alone for clinical decisions.
# ============================================================


CPIC_RECOMMENDATION_RULES: Dict[str, Dict[str, Dict[str, str]]] = {
    "CYP2C19": {
        "Clopidogrel": {
            "Poor Metabolizer":
                "Avoid / use alternative agent",

            "Intermediate Metabolizer":
                "Consider alternative agent or guideline-directed strategy",

            "Normal Metabolizer":
                "Use standard clopidogrel therapy",

            "Rapid Metabolizer":
                "Use standard clopidogrel therapy",

            "Ultrarapid Metabolizer":
                "Use standard clopidogrel therapy",
        }
    }
}


def get_recommendation_rule(
    gene: str,
    drug: str,
    phenotype: Optional[str],
) -> Optional[str]:
    """
    Look up a recommendation in the local fallback rules.

    Returns None when no matching rule is available.
    """

    if not phenotype:
        return None

    gene_rules = CPIC_RECOMMENDATION_RULES.get(
        gene,
        {},
    )

    drug_rules = gene_rules.get(
        drug,
        {},
    )

    return drug_rules.get(phenotype)


def determine_evidence_level(
    evidence: Dict[str, Any],
) -> Optional[str]:
    """
    Return the evidence label provided by the evidence sources.

    CPIC/ClinPGx is preferred when it is available.
    Note: a label such as 'Strong' may represent recommendation
    classification, not necessarily an A-D evidence level.
    """

    cpic = evidence.get("cpic") or {}
    pharmgkb = evidence.get("pharmgkb") or {}

    cpic_level = cpic.get("evidence_level")

    if cpic.get("available") and cpic_level:
        return f"CPIC {cpic_level}"

    pharmgkb_level = pharmgkb.get("evidence_level")

    if pharmgkb.get("available") and pharmgkb_level:
        return f"PharmGKB {pharmgkb_level}"

    # Preserve a supplied label even if the source's availability
    # flag is missing or false.
    if cpic_level:
        return f"CPIC {cpic_level}"

    if pharmgkb_level:
        return f"PharmGKB {pharmgkb_level}"

    return None


def determine_source(
    evidence: Dict[str, Any],
) -> Optional[str]:
    """
    Identify the evidence source used for the recommendation.
    """

    cpic = evidence.get("cpic") or {}

    if cpic.get("available"):
        return "CPIC"

    pharmgkb = evidence.get("pharmgkb") or {}

    if pharmgkb.get("available"):
        return "PharmGKB"

    return None


def build_recommendation(
    evidence: Dict[str, Any],
    conflict_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build one structured pharmacogenomic recommendation.

    Priority:
    1. Use an available CPIC/ClinPGx recommendation.
    2. Otherwise, use a local development fallback rule.
    3. If neither exists, report that no recommendation is available.

    This function does not use an LLM.
    """

    pair = evidence.get("gene_drug_pair") or {}

    gene = pair.get("gene")
    drug = pair.get("drug")

    diplotype = pair.get("diplotype")
    phenotype = pair.get("phenotype")
    activity_score = pair.get("activity_score")

    # --------------------------------------------------------
    # 1. Prefer the recommendation retrieved from CPIC/ClinPGx.
    # --------------------------------------------------------

    cpic = evidence.get("cpic") or {}

    cpic_recommendation = cpic.get("recommendation")

    if (
        cpic.get("available")
        and isinstance(cpic_recommendation, str)
        and cpic_recommendation.strip()
    ):
        recommendation = cpic_recommendation.strip()
        source = "CPIC"

    else:
        # ----------------------------------------------------
        # 2. Fall back to the local development rules.
        # ----------------------------------------------------

        recommendation = get_recommendation_rule(
            gene=gene,
            drug=drug,
            phenotype=phenotype,
        )

        source = determine_source(evidence)

    # --------------------------------------------------------
    # Evidence label
    # --------------------------------------------------------

    evidence_level = determine_evidence_level(evidence)

    # --------------------------------------------------------
    # Conflict information
    # --------------------------------------------------------

    conflict_result = conflict_result or {}

    has_conflict = conflict_result.get(
        "conflict",
        False,
    )

    requires_review = conflict_result.get(
        "requires_review",
        False,
    )

    conflicts = conflict_result.get(
        "conflicts",
        [],
    )

    warnings = conflict_result.get(
        "warnings",
        [],
    )

    # --------------------------------------------------------
    # 3. Do not invent a recommendation when no rule or source
    #    recommendation is available.
    # --------------------------------------------------------

    if recommendation is None:
        recommendation = (
            "No rule-based recommendation available "
            "for this gene-drug-phenotype combination."
        )

    return {
        "drug": drug,
        "gene": gene,
        "diplotype": diplotype,
        "phenotype": phenotype,
        "activity_score": activity_score,
        "recommendation": recommendation,
        "evidence_level": evidence_level,
        "source": source,
        "conflict": has_conflict,
        "requires_review": requires_review,
        "conflicts": conflicts,
        "warnings": warnings,
    }


def build_recommendations(
    evidence_packages: List[Dict[str, Any]],
    conflict_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Build recommendations for all gene-drug evidence packages.
    """

    recommendations: List[Dict[str, Any]] = []

    for evidence in evidence_packages:
        pair = evidence.get("gene_drug_pair") or {}

        gene = pair.get("gene")
        drug = pair.get("drug")

        matching_conflict = next(
            (
                result
                for result in conflict_results
                if result.get("gene") == gene
                and result.get("drug") == drug
            ),
            None,
        )

        recommendation = build_recommendation(
            evidence=evidence,
            conflict_result=matching_conflict,
        )

        recommendations.append(recommendation)

    return recommendations
