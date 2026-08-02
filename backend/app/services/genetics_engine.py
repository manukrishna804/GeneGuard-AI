"""
services/genetics_engine.py
============================
Reusable genetics inference engine for GeneGuard-AI.

Provides:
  - punnett_square()             — probability calculation for Mendelian inheritance
  - detect_inheritance_pattern() — rule-based pattern detector from pedigree data

This module has NO database or API dependencies — it operates purely on in-memory
data structures so it can be called from any service or test without a DB session.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Types / Enums
# ---------------------------------------------------------------------------

class InheritanceMode(str, Enum):
    AUTOSOMAL_RECESSIVE = "autosomal_recessive"
    AUTOSOMAL_DOMINANT  = "autosomal_dominant"
    X_LINKED_RECESSIVE  = "x_linked_recessive"   # future use
    UNKNOWN             = "unknown"


class CarrierStatus(str, Enum):
    CARRIER     = "carrier"       # heterozygous, one affected allele
    AFFECTED    = "affected"      # homozygous affected / compound het
    UNAFFECTED  = "unaffected"    # homozygous normal
    UNKNOWN     = "unknown"


@dataclass
class PedigreeNode:
    """Lightweight representation of a family member for engine calculations."""
    member_id: int
    sex: str                                       # "M", "F", "Unknown"
    health_status: str                             # "Affected", "Unaffected", "Unknown"
    carrier_status: Optional[Dict[str, bool]] = field(default_factory=dict)
    parent_id: Optional[int] = None
    relationship_label: Optional[str] = None
    diagnosed_conditions: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Punnett Square Calculator
# ---------------------------------------------------------------------------

def punnett_square(
    parent1_status: CarrierStatus,
    parent2_status: CarrierStatus,
    mode: InheritanceMode = InheritanceMode.AUTOSOMAL_RECESSIVE,
) -> Dict[str, float]:
    """
    Calculate offspring probability distribution using simplified Punnett square logic.

    For autosomal recessive:
        - Affected (aa) × Affected (aa)  → 100% Affected
        - Affected (aa) × Carrier  (Aa)  → 50% Affected, 50% Carrier
        - Affected (aa) × Unaffected(AA) → 100% Carrier
        - Carrier  (Aa) × Carrier  (Aa)  → 25% Affected, 50% Carrier, 25% Unaffected
        - Carrier  (Aa) × Unaffected(AA) → 50% Carrier, 50% Unaffected
        - Unaffected(AA)× Unaffected(AA) → 100% Unaffected

    For autosomal dominant:
        - Affected (Aa) × Unaffected(AA) → 50% Affected, 50% Unaffected
        - Affected (Aa) × Affected (Aa)  → 75% Affected, 25% Unaffected
        - Unaffected(AA)× Unaffected(AA) → 100% Unaffected
        (Assuming incomplete penetrance model: one dominant allele = affected)

    Returns:
        dict with keys "affected", "carrier", "unaffected" as float probabilities (sum = 1.0)
    """
    p1, p2 = parent1_status, parent2_status
    # Normalize order so p1 <= p2 (alphabetical) to reduce branching
    key = tuple(sorted([p1.value, p2.value]))

    if mode == InheritanceMode.AUTOSOMAL_RECESSIVE:
        table: Dict[tuple, Dict[str, float]] = {
            ("affected",  "affected"):   {"affected": 1.00, "carrier": 0.00, "unaffected": 0.00},
            ("affected",  "carrier"):    {"affected": 0.50, "carrier": 0.50, "unaffected": 0.00},
            ("affected",  "unaffected"): {"affected": 0.00, "carrier": 1.00, "unaffected": 0.00},
            ("carrier",   "carrier"):    {"affected": 0.25, "carrier": 0.50, "unaffected": 0.25},
            ("carrier",   "unaffected"): {"affected": 0.00, "carrier": 0.50, "unaffected": 0.50},
            ("unaffected","unaffected"): {"affected": 0.00, "carrier": 0.00, "unaffected": 1.00},
            # unknown parent — return 50/50 estimate
            ("affected",  "unknown"):    {"affected": 0.50, "carrier": 0.25, "unaffected": 0.25},
            ("carrier",   "unknown"):    {"affected": 0.125,"carrier": 0.375,"unaffected": 0.50},
            ("unknown",   "unknown"):    {"affected": 0.25, "carrier": 0.50, "unaffected": 0.25},
            ("unaffected","unknown"):    {"affected": 0.00, "carrier": 0.25, "unaffected": 0.75},
        }

    elif mode == InheritanceMode.AUTOSOMAL_DOMINANT:
        # In dominant mode "carrier" is equivalent to "affected" (one allele suffices)
        table = {
            ("affected",  "affected"):   {"affected": 0.75, "carrier": 0.00, "unaffected": 0.25},
            ("affected",  "unaffected"): {"affected": 0.50, "carrier": 0.00, "unaffected": 0.50},
            ("unaffected","unaffected"): {"affected": 0.00, "carrier": 0.00, "unaffected": 1.00},
            ("affected",  "unknown"):    {"affected": 0.50, "carrier": 0.00, "unaffected": 0.50},
            ("unaffected","unknown"):    {"affected": 0.25, "carrier": 0.00, "unaffected": 0.75},
            ("unknown",   "unknown"):    {"affected": 0.50, "carrier": 0.00, "unaffected": 0.50},
            # carrier treated same as affected in dominant
            ("affected",  "carrier"):    {"affected": 0.75, "carrier": 0.00, "unaffected": 0.25},
            ("carrier",   "carrier"):    {"affected": 0.75, "carrier": 0.00, "unaffected": 0.25},
            ("carrier",   "unaffected"): {"affected": 0.50, "carrier": 0.00, "unaffected": 0.50},
            ("carrier",   "unknown"):    {"affected": 0.50, "carrier": 0.00, "unaffected": 0.50},
        }

    else:
        # Fallback for unsupported modes — return uniform uncertainty
        return {"affected": 0.33, "carrier": 0.34, "unaffected": 0.33}

    result = table.get(key)
    if result is None:
        return {"affected": 0.25, "carrier": 0.50, "unaffected": 0.25}

    return result


# ---------------------------------------------------------------------------
# Inheritance Pattern Detector
# ---------------------------------------------------------------------------

def detect_inheritance_pattern(
    members: List[PedigreeNode],
) -> Dict[str, object]:
    """
    Rule-based inheritance pattern detector, using disqualifying evidence
    rather than loose pattern-matching.

    Approach: for each affected member whose parent's health status is known,
    classify that parent-child relationship as evidence FOR or AGAINST each
    candidate pattern. A pattern is disqualified if there is direct evidence
    against it (e.g. an affected father passing to an affected son rules out
    X-linked recessive; an affected child of two unaffected parents rules out
    clean autosomal dominant). Remaining candidates are then scored by amount
    of supporting evidence, and confidence is downgraded when evidence is
    sparse or tied between competing patterns.
    """
    if not members:
        return _pattern_result(InheritanceMode.UNKNOWN.value, "low",
                                "No pedigree data provided.", 0, 0)

    id_map = {m.member_id: m for m in members}
    affected = [m for m in members if m.health_status == "Affected"]
    unaffected = [m for m in members if m.health_status == "Unaffected"]
    n_affected, n_unaffected = len(affected), len(unaffected)

    if n_affected == 0:
        return _pattern_result(InheritanceMode.UNKNOWN.value, "low",
                                "No affected members found in pedigree.",
                                0, n_unaffected)

    dominant_supporting = dominant_against = 0
    recessive_supporting = 0
    xlinked_supporting = 0
    male_to_male_transmission = False  # disqualifies X-linked recessive

    for m in members:
        if m.parent_id is None or m.parent_id not in id_map:
            continue
        parent = id_map[m.parent_id]
        if parent.health_status not in ("Affected", "Unaffected"):
            continue  # parent status unknown -> not informative

        if m.health_status == "Affected":
            if parent.health_status == "Affected":
                dominant_supporting += 1
                if parent.sex == "M" and m.sex == "M":
                    male_to_male_transmission = True
            else:  # parent unaffected, child affected -> generation skip
                dominant_against += 1
                recessive_supporting += 1
                if m.sex == "M" and parent.sex == "F":
                    xlinked_supporting += 1

    dominant_disqualified = dominant_against > 0
    xlinked_disqualified = male_to_male_transmission

    affected_males = [m for m in affected if m.sex == "M"]
    affected_females = [m for m in affected if m.sex == "F"]
    only_males_affected = bool(affected_males) and not affected_females

    candidates = []

    if not dominant_disqualified and dominant_supporting > 0:
        conf = "high" if dominant_supporting >= 2 else "moderate"
        candidates.append((
            InheritanceMode.AUTOSOMAL_DOMINANT.value, conf, dominant_supporting,
            f"{dominant_supporting} affected member(s) have an affected parent "
            "with no observed generation-skipping, consistent with autosomal "
            "dominant inheritance."
        ))

    if not xlinked_disqualified and only_males_affected and xlinked_supporting > 0:
        conf = "high" if xlinked_supporting >= 2 else "moderate"
        candidates.append((
            InheritanceMode.X_LINKED_RECESSIVE.value, conf, xlinked_supporting,
            "Only male members are affected, transmitted through unaffected "
            f"(likely carrier) mothers, with no father-to-son transmission "
            f"observed ({xlinked_supporting} informative case(s)) -- consistent "
            "with X-linked recessive inheritance."
        ))

    if recessive_supporting > 0:
        conf = "high" if recessive_supporting >= 2 else "moderate"
        candidates.append((
            InheritanceMode.AUTOSOMAL_RECESSIVE.value, conf, recessive_supporting,
            f"{recessive_supporting} affected member(s) born to two unaffected "
            "(carrier) parents, consistent with autosomal recessive inheritance."
        ))

    if not candidates:
        return _pattern_result(
            InheritanceMode.UNKNOWN.value, "low",
            "Insufficient or ambiguous pedigree data (parents' status unknown "
            "or too few informative relationships) to determine inheritance "
            "pattern confidently. Consider adding more family members or "
            "health status information.",
            n_affected, n_unaffected,
        )

    candidates.sort(key=lambda c: c[2], reverse=True)
    pattern, confidence, top_score, rationale = candidates[0]

    if len(candidates) > 1 and candidates[1][2] == top_score:
        confidence = "low"
        rationale += (" (Note: evidence is ambiguous between multiple "
                       "patterns; treat with caution.)")

    return _pattern_result(pattern, confidence, rationale, n_affected, n_unaffected)


def _pattern_result(pattern: str, confidence: str, rationale: str,
                     affected_count: int, unaffected_count: int) -> Dict[str, object]:
    return {
        "pattern": pattern,
        "confidence": confidence,
        "rationale": rationale,
        "affected_count": affected_count,
        "unaffected_count": unaffected_count,
    }


# ---------------------------------------------------------------------------
# Helper — convert DB model list to PedigreeNode list
# ---------------------------------------------------------------------------

def family_history_to_pedigree(members: list) -> List[PedigreeNode]:
    """
    Converts a list of FamilyHistory ORM objects to PedigreeNode dataclasses
    so the engine stays decoupled from SQLAlchemy models.
    """
    return [
        PedigreeNode(
            member_id=m.id,
            sex=m.sex or "Unknown",
            health_status=m.health_status or "Unknown",
            carrier_status=m.carrier_status or {},
            parent_id=m.parent_id,
            relationship_label=m.relationship_label,
            diagnosed_conditions=m.diagnosed_conditions or [],
        )
        for m in members
    ]