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
    Rule-based heuristic to infer the most likely inheritance pattern given a
    pedigree (list of PedigreeNode).

    Rules applied (in priority order):
      1. If affected individuals appear in every generation → likely Autosomal Dominant
      2. If only siblings are affected (parents unaffected) → likely Autosomal Recessive
      3. If only male members are affected → consider X-linked Recessive
      4. If pattern is unclear → Unknown

    Returns:
        {
            "pattern":    str  (InheritanceMode value),
            "confidence": str  ("high", "moderate", "low"),
            "rationale":  str  (human-readable explanation),
            "affected_count":   int,
            "unaffected_count": int,
        }
    """
    if not members:
        return {
            "pattern": InheritanceMode.UNKNOWN.value,
            "confidence": "low",
            "rationale": "No pedigree data provided.",
            "affected_count": 0,
            "unaffected_count": 0,
        }

    affected   = [m for m in members if m.health_status == "Affected"]
    unaffected = [m for m in members if m.health_status == "Unaffected"]
    unknown    = [m for m in members if m.health_status not in ("Affected", "Unaffected")]

    n_affected   = len(affected)
    n_unaffected = len(unaffected)

    if n_affected == 0:
        return {
            "pattern": InheritanceMode.UNKNOWN.value,
            "confidence": "low",
            "rationale": "No affected members found in pedigree.",
            "affected_count": 0,
            "unaffected_count": n_unaffected,
        }

    # Build parent→children map
    parent_map: Dict[Optional[int], List[PedigreeNode]] = {}
    for m in members:
        parent_map.setdefault(m.parent_id, []).append(m)

    # Collect unique generations by tracing depth from roots
    def depth(node: PedigreeNode, id_map: Dict[int, PedigreeNode], cache: Dict[int, int]) -> int:
        if node.member_id in cache:
            return cache[node.member_id]
        if node.parent_id is None or node.parent_id not in id_map:
            cache[node.member_id] = 0
            return 0
        d = 1 + depth(id_map[node.parent_id], id_map, cache)
        cache[node.member_id] = d
        return d

    id_map = {m.member_id: m for m in members}
    depth_cache: Dict[int, int] = {}
    affected_generations = {depth(m, id_map, depth_cache) for m in affected}
    total_generations    = {depth(m, id_map, depth_cache) for m in members}

    # Rule 1 — Autosomal Dominant: affected in multiple generations
    if len(affected_generations) >= 2 and len(affected_generations) >= len(total_generations) / 2:
        return {
            "pattern": InheritanceMode.AUTOSOMAL_DOMINANT.value,
            "confidence": "high" if len(affected_generations) >= 3 else "moderate",
            "rationale": (
                f"Affected individuals span {len(affected_generations)} generation(s), "
                "suggesting vertical transmission consistent with autosomal dominant inheritance."
            ),
            "affected_count": n_affected,
            "unaffected_count": n_unaffected,
        }

    # Rule 2 — X-linked Recessive: only males affected
    affected_males   = [m for m in affected if m.sex == "M"]
    affected_females = [m for m in affected if m.sex == "F"]

    if affected_males and not affected_females:
        return {
            "pattern": InheritanceMode.X_LINKED_RECESSIVE.value,
            "confidence": "moderate",
            "rationale": (
                f"All {len(affected_males)} affected member(s) are male with no affected females, "
                "consistent with X-linked recessive inheritance."
            ),
            "affected_count": n_affected,
            "unaffected_count": n_unaffected,
        }

    # Rule 3 — Autosomal Recessive: affected only among siblings, parents unaffected
    root_affected = [m for m in affected if m.parent_id is None]
    if not root_affected and n_affected >= 1:
        return {
            "pattern": InheritanceMode.AUTOSOMAL_RECESSIVE.value,
            "confidence": "moderate",
            "rationale": (
                f"{n_affected} affected member(s) found among non-root nodes with unaffected "
                "ancestors, consistent with autosomal recessive inheritance."
            ),
            "affected_count": n_affected,
            "unaffected_count": n_unaffected,
        }

    # Fallback
    return {
        "pattern": InheritanceMode.UNKNOWN.value,
        "confidence": "low",
        "rationale": (
            "Insufficient or ambiguous pedigree data to determine inheritance pattern. "
            "Consider adding more family members or health status information."
        ),
        "affected_count": n_affected,
        "unaffected_count": n_unaffected,
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
