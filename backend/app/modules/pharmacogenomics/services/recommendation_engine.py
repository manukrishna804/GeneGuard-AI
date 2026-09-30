from typing import Any, Dict, List, Optional


# ============================================================
# INITIAL RECOMMENDATION RULES
# ============================================================
#
# These are development rules for the first working pipeline.
#
# The final clinical recommendation rules should come from
# validated CPIC guideline data and should NOT be treated as
# a substitute for the official guideline.
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
    Look up a recommendation using the current local
    rule set.

    Returns None when no rule is available.
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
    Determine the evidence label available for the
    recommendation.

    CPIC is treated as the primary guideline source
    when valid CPIC evidence is available.

    This function does not override source evidence.
    """

    cpic = evidence.get("cpic") or {}
    pharmgkb = evidence.get("pharmgkb") or {}

    cpic_level = cpic.get("evidence_level")

    if cpic_level:
        return f"CPIC {cpic_level}"

    pharmgkb_level = pharmgkb.get(
        "evidence_level"
    )

    if pharmgkb_level:
        return f"PharmGKB {pharmgkb_level}"

    return None


def determine_source(
    evidence: Dict[str, Any],
) -> Optional[str]:
    """
    Identify the source supporting the recommendation.
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

    This is the rule-engine stage.

    The function does not use an LLM.
    """

    pair = evidence.get(
        "gene_drug_pair",
        {},
    )

    gene = pair.get("gene")
    drug = pair.get("drug")

    diplotype = pair.get("diplotype")
    phenotype = pair.get("phenotype")
    activity_score = pair.get(
        "activity_score"
    )

    recommendation = get_recommendation_rule(
        gene=gene,
        drug=drug,
        phenotype=phenotype,
    )

    evidence_level = determine_evidence_level(
        evidence
    )

    source = determine_source(
        evidence
    )

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
    # If no validated rule is currently available, don't
    # invent a recommendation.
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
    Build recommendations for all gene-drug evidence
    packages.
    """

    recommendations: List[Dict[str, Any]] = []

    for evidence in evidence_packages:

        pair = evidence.get(
            "gene_drug_pair",
            {},
        )

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

        recommendations.append(
            recommendation
        )

    return recommendations