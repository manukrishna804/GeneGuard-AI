
from typing import Any, Dict, List, Optional


# ============================================================
# EVIDENCE LEVEL PRIORITY
# ============================================================
#
# These priority values are used only when the source provides
# the corresponding evidence-level format.
#
# CPIC evidence levels:
#     A > B > C > D
#
# PharmGKB evidence levels:
#     1A > 1B > 2A > 2B > 3 > 4
#
# ClinPGx recommendation classifications such as Strong,
# Moderate, and No Recommendation are NOT CPIC A-D levels.
# They are therefore not compared using CPIC_LEVEL_PRIORITY.
# ============================================================


CPIC_LEVEL_PRIORITY = {
    "A": 4,
    "B": 3,
    "C": 2,
    "D": 1,
}


PHARMGKB_LEVEL_PRIORITY = {
    "1A": 6,
    "1B": 5,
    "2A": 4,
    "2B": 3,
    "3": 2,
    "4": 1,
}


# Classifications returned by the ClinPGx recommendation endpoint.
# These are not equivalent to CPIC A-D evidence levels.
CPIC_RECOMMENDATION_CLASSIFICATIONS = {
    "STRONG",
    "MODERATE",
    "NO RECOMMENDATION",
}


def normalize_level(
    level: Optional[str],
) -> Optional[str]:
    """
    Normalize an evidence-level or classification string.

    Examples:
        "CPIC A"       -> "A"
        "A"            -> "A"
        "PharmGKB 1A"  -> "1A"
        "Strong"       -> "STRONG"
    """

    if not isinstance(level, str) or not level.strip():
        return None

    normalized = level.strip().upper()

    for prefix in ("CPIC ", "PHARMGKB "):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
            break

    return normalized or None


def check_cpic_evidence(
    cpic: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Check CPIC/ClinPGx evidence availability.

    Distinguishes a recognized A-D evidence level from a
    ClinPGx recommendation classification such as Strong.
    """

    if not cpic or not cpic.get("available"):
        return {
            "available": False,
            "valid": False,
            "level": None,
            "classification": None,
            "level_type": None,
        }

    raw_level = cpic.get("evidence_level")
    level = normalize_level(raw_level)

    if level in CPIC_LEVEL_PRIORITY:
        return {
            "available": True,
            "valid": True,
            "level": level,
            "classification": None,
            "level_type": "cpic_evidence_level",
        }

    if level in CPIC_RECOMMENDATION_CLASSIFICATIONS:
        return {
            "available": True,
            "valid": True,
            "level": None,
            "classification": level.title(),
            "level_type": "clinpgx_recommendation_classification",
        }

    return {
        "available": True,
        "valid": False,
        "level": None,
        "classification": None,
        "level_type": None,
    }


def check_pharmgkb_evidence(
    pharmgkb: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Check whether PharmGKB evidence is available and whether
    its evidence level matches a recognized PharmGKB category.
    """

    if not pharmgkb or not pharmgkb.get("available"):
        return {
            "available": False,
            "valid": False,
            "level": None,
        }

    level = normalize_level(
        pharmgkb.get("evidence_level")
    )

    return {
        "available": True,
        "valid": level in PHARMGKB_LEVEL_PRIORITY,
        "level": level,
    }


def detect_conflict(
    evidence: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Detect missing evidence and comparable evidence-level
    differences for one gene-drug pair.

    This function does not determine clinical treatment.
    """

    conflicts: List[Dict[str, Any]] = []
    warnings: List[str] = []

    cpic = check_cpic_evidence(
        evidence.get("cpic")
    )

    pharmgkb = check_pharmgkb_evidence(
        evidence.get("pharmgkb")
    )

    # --------------------------------------------------------
    # CPIC / ClinPGx evidence checks
    # --------------------------------------------------------

    if cpic["available"] and not cpic["valid"]:
        warnings.append(
            "CPIC evidence label is missing or unrecognized."
        )

    # A ClinPGx classification such as Strong is valid as a
    # recommendation classification, but it is not converted
    # into an A-D evidence level.
    if (
        cpic["available"]
        and cpic["level_type"]
        == "clinpgx_recommendation_classification"
    ):
        pass

    # --------------------------------------------------------
    # PharmGKB evidence checks
    # --------------------------------------------------------

    if pharmgkb["available"] and not pharmgkb["valid"]:
        warnings.append(
            "PharmGKB evidence level is missing or unrecognized."
        )

    # --------------------------------------------------------
    # Compare evidence levels only when both sources provide
    # comparable, recognized evidence-level formats.
    # --------------------------------------------------------

    if (
        cpic["available"]
        and pharmgkb["available"]
        and cpic["level"] is not None
        and pharmgkb["level"] is not None
        and cpic["level"] in CPIC_LEVEL_PRIORITY
        and pharmgkb["level"] in PHARMGKB_LEVEL_PRIORITY
    ):
        if cpic["level"] != pharmgkb["level"]:
            conflicts.append(
                {
                    "type": "evidence_level_difference",
                    "cpic_level": cpic["level"],
                    "pharmgkb_level": pharmgkb["level"],
                    "message": (
                        "CPIC and PharmGKB report different "
                        "evidence-level labels. These labels "
                        "come from different systems and should "
                        "not be interpreted as directly equivalent."
                    ),
                }
            )

    # --------------------------------------------------------
    # Missing primary evidence
    # --------------------------------------------------------

    if not cpic["available"]:
        warnings.append("CPIC evidence is unavailable.")

    if not pharmgkb["available"]:
        warnings.append("PharmGKB evidence is unavailable.")

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    has_conflict = bool(conflicts)

    requires_review = bool(
        has_conflict or warnings
    )

    return {
        "conflict": has_conflict,
        "requires_review": requires_review,
        "conflicts": conflicts,
        "warnings": warnings,
    }


def detect_multiple_conflicts(
    evidence_packages: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Run conflict detection across multiple gene-drug
    evidence packages.
    """

    results: List[Dict[str, Any]] = []

    for evidence in evidence_packages:
        result = detect_conflict(evidence)

        gene_drug_pair = evidence.get(
            "gene_drug_pair"
        ) or {}

        results.append(
            {
                "gene": gene_drug_pair.get("gene"),
                "drug": gene_drug_pair.get("drug"),
                **result,
            }
        )

    return results
