
from typing import Any, Dict, List


def has_usable_value(value: Any) -> bool:
    """Check whether a value contains meaningful, non-empty data."""

    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, dict):
        return any(has_usable_value(v) for v in value.values())

    if isinstance(value, list):
        return any(has_usable_value(v) for v in value)

    return True


def has_pharmvar_definition(pharmvar: Any) -> bool:
    """Only count PharmVar entries with actual definitions."""

    if not isinstance(pharmvar, list):
        return False

    return any(
        isinstance(item, dict)
        and has_usable_value(item.get("definition"))
        for item in pharmvar
    )


def calculate_confidence(
    recommendations: List[Dict[str, Any]],
) -> float:
    """
    Calculate an engineering evidence-completeness score.

    This is NOT a clinical probability or a validated measure
    of recommendation accuracy.
    """

    if not recommendations:
        return 0.0

    scores: List[float] = []

    for recommendation in recommendations:
        score = 0.0
        evidence = recommendation.get("evidence") or {}

        cpic = evidence.get("cpic") or {}
        pharmgkb = evidence.get("pharmgkb") or {}
        pharmvar = evidence.get("pharmvar") or []
        drugbank = evidence.get("drugbank") or {}

        # Recommendation text exists.
        if has_usable_value(recommendation.get("recommendation")):
            score += 30

        # CPIC recommendation or implication is actually available.
        if (
            cpic.get("available")
            and (
                has_usable_value(cpic.get("recommendation"))
                or has_usable_value(cpic.get("implication"))
            )
        ):
            score += 30

        # PharmGKB contains usable evidence.
        if (
            pharmgkb.get("available")
            and (
                has_usable_value(pharmgkb.get("annotation"))
                or has_usable_value(pharmgkb.get("evidence_level"))
            )
        ):
            score += 20

        # PharmVar must contain an actual allele definition.
        if has_pharmvar_definition(pharmvar):
            score += 10

        # DrugBank must contain usable interaction or context data.
        if (
            drugbank.get("available")
            and (
                has_usable_value(drugbank.get("interaction"))
                or has_usable_value(
                    drugbank.get("pharmacokinetic_context")
                )
            )
        ):
            score += 5

        # Penalize explicitly detected conflicts.
        if recommendation.get("conflict"):
            score -= 20

        score = max(0.0, min(100.0, score))
        scores.append(score)

    return round(sum(scores) / len(scores), 2)


def calculate_evidence_confidence(
    evidence: Dict[str, Any],
) -> float:
    """
    Calculate an engineering evidence-completeness score
    for one evidence package. This function is not currently
    used by the main pipeline.
    """

    score = 0.0

    cpic = evidence.get("cpic") or {}
    pharmgkb = evidence.get("pharmgkb") or {}
    pharmvar = evidence.get("pharmvar") or []
    drugbank = evidence.get("drugbank") or {}

    if (
        cpic.get("available")
        and (
            has_usable_value(cpic.get("recommendation"))
            or has_usable_value(cpic.get("implication"))
        )
    ):
        score += 40

    if (
        pharmgkb.get("available")
        and (
            has_usable_value(pharmgkb.get("annotation"))
            or has_usable_value(pharmgkb.get("evidence_level"))
        )
    ):
        score += 25

    if has_pharmvar_definition(pharmvar):
        score += 20

    if (
        drugbank.get("available")
        and (
            has_usable_value(drugbank.get("interaction"))
            or has_usable_value(
                drugbank.get("pharmacokinetic_context")
            )
        )
    ):
        score += 15

    return round(min(100.0, score), 2)
