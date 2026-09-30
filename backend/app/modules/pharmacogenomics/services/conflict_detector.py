from typing import Any, Dict, List, Optional


# ============================================================
# EVIDENCE LEVEL PRIORITY
# ============================================================
#
# Higher number = stronger evidence.
#
# CPIC:
#     A > B > C > D
#
# PharmGKB:
#     1A > 1B > 2A > 2B > 3 > 4
#
# These are used only to identify differences in evidence
# strength. They are NOT used by this file to make a
# clinical recommendation.
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


def normalize_level(
    level: Optional[str],
) -> Optional[str]:
    """
    Normalize an evidence-level string.

    Examples:

        "CPIC A" -> "A"
        "A"      -> "A"
        "1A"     -> "1A"
    """

    if not level:
        return None

    level = level.strip().upper()

    if level.startswith("CPIC "):
        level = level.replace("CPIC ", "", 1)

    if level.startswith("PHARMGKB "):
        level = level.replace(
            "PHARMGKB ",
            "",
            1,
        )

    return level


def check_cpic_evidence(
    cpic: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Check whether CPIC evidence is available and whether
    its evidence level is recognized.
    """

    if not cpic:
        return {
            "available": False,
            "valid": False,
            "level": None,
        }

    if not cpic.get("available"):
        return {
            "available": False,
            "valid": False,
            "level": None,
        }

    level = normalize_level(
        cpic.get("evidence_level")
    )

    return {
        "available": True,
        "valid": level in CPIC_LEVEL_PRIORITY,
        "level": level,
    }


def check_pharmgkb_evidence(
    pharmgkb: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Check whether PharmGKB evidence is available and
    whether its evidence level is recognized.
    """

    if not pharmgkb:
        return {
            "available": False,
            "valid": False,
            "level": None,
        }

    if not pharmgkb.get("available"):
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
    Detect evidence conflicts or missing evidence for a
    single gene-drug pair.

    IMPORTANT:
    This function does not select a clinical winner.
    It only identifies evidence differences or problems
    that should be handled by the recommendation stage.
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
    # CPIC evidence checks
    # --------------------------------------------------------

    if cpic["available"] and not cpic["valid"]:
        warnings.append(
            "CPIC evidence level is missing or unrecognized."
        )

    # --------------------------------------------------------
    # PharmGKB evidence checks
    # --------------------------------------------------------

    if (
        pharmgkb["available"]
        and not pharmgkb["valid"]
    ):
        warnings.append(
            "PharmGKB evidence level is missing or "
            "unrecognized."
        )

    # --------------------------------------------------------
    # Compare CPIC and PharmGKB evidence availability
    # --------------------------------------------------------

    if cpic["available"] and pharmgkb["available"]:

        cpic_priority = CPIC_LEVEL_PRIORITY.get(
            cpic["level"]
        )

        pharmgkb_priority = PHARMGKB_LEVEL_PRIORITY.get(
            pharmgkb["level"]
        )

        if (
            cpic_priority is not None
            and pharmgkb_priority is not None
        ):

            # We are detecting a difference in evidence
            # strength, not declaring either source correct
            # or incorrect.

            if cpic["level"] != pharmgkb["level"]:

                conflicts.append(
                    {
                        "type": "evidence_level_difference",
                        "cpic_level": cpic["level"],
                        "pharmgkb_level": pharmgkb["level"],
                        "message": (
                            "CPIC and PharmGKB report "
                            "different evidence levels."
                        ),
                    }
                )

    # --------------------------------------------------------
    # Missing primary evidence
    # --------------------------------------------------------

    if not cpic["available"]:
        warnings.append(
            "CPIC evidence is unavailable."
        )

    if not pharmgkb["available"]:
        warnings.append(
            "PharmGKB evidence is unavailable."
        )

    # --------------------------------------------------------
    # Determine final conflict status
    # --------------------------------------------------------

    has_conflict = len(conflicts) > 0

    requires_review = (
        has_conflict
        or len(warnings) > 0
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
            "gene_drug_pair",
            {},
        )

        results.append(
            {
                "gene": gene_drug_pair.get("gene"),
                "drug": gene_drug_pair.get("drug"),
                **result,
            }
        )

    return results