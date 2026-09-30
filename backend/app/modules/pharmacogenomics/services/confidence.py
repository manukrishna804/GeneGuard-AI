from typing import Any, Dict, List


def calculate_confidence(
    recommendations: List[Dict[str, Any]],
) -> float:
    """
    Calculate an overall confidence score for the
    pharmacogenomic analysis.

    The score is based on:
    - availability of CPIC evidence
    - availability of PharmGKB evidence
    - availability of PharmVar evidence
    - availability of DrugBank context
    - presence of evidence conflicts
    - availability of a rule-based recommendation

    This is an engineering confidence indicator for the
    Module 5 result. It is NOT a clinical probability.
    """

    if not recommendations:
        return 0.0

    scores: List[float] = []

    for recommendation in recommendations:

        score = 0.0

        # ----------------------------------------------------
        # Recommendation exists
        # ----------------------------------------------------

        if recommendation.get("recommendation"):
            score += 30

        # ----------------------------------------------------
        # Evidence source
        # ----------------------------------------------------

        evidence = recommendation.get(
            "evidence",
            {},
        )

        if evidence.get("cpic", {}).get("available"):
            score += 30

        if evidence.get("pharmgkb", {}).get("available"):
            score += 20

        if evidence.get("pharmvar"):
            score += 10

        if evidence.get("drugbank", {}).get("available"):
            score += 5

        # ----------------------------------------------------
        # Conflict penalty
        # ----------------------------------------------------

        if recommendation.get("conflict"):
            score -= 20

        # Keep each recommendation between 0 and 100.
        score = max(
            0.0,
            min(100.0, score),
        )

        scores.append(score)

    return round(
        sum(scores) / len(scores),
        2,
    )


def calculate_evidence_confidence(
    evidence: Dict[str, Any],
) -> float:
    """
    Calculate confidence for a single evidence package.

    This function is useful when the pipeline needs to
    inspect confidence before generating the final report.
    """

    score = 0.0

    cpic = evidence.get("cpic") or {}
    pharmgkb = evidence.get("pharmgkb") or {}
    pharmvar = evidence.get("pharmvar") or []
    drugbank = evidence.get("drugbank") or {}

    if cpic.get("available"):
        score += 40

    if pharmgkb.get("available"):
        score += 25

    if pharmvar:
        score += 20

    if drugbank.get("available"):
        score += 15

    return round(
        min(100.0, score),
        2,
    )