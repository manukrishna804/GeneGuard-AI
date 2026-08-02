"""
api/v1/endpoints/consanguinity.py
==================================
Module 4 -- Consanguineous Marriage & Child Genetic Risk (direct calculator).

Unlike Module 6 (family_history), this endpoint does NOT require building a
full family tree first. It's the simpler, direct entry point: given two
parents' known (or estimated) carrier status for a specific condition, plus
optional relationship-type context, return the offspring probability
breakdown immediately.

This is intentionally stateless -- no new database table. It reuses the same
punnett_square() engine that powers Module 6's /analyze endpoint, so both
modules stay mathematically consistent by construction (see
services/genetics_engine.py).
"""
from __future__ import annotations

from typing import Optional

# pyrefly: ignore [missing-import]
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.genetics_engine import (
    CarrierStatus,
    InheritanceMode,
    punnett_square,
)

router = APIRouter(
    prefix="/consanguinity",
    tags=["Consanguinity / Family Planning"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ConsanguinityRequest(BaseModel):
    condition_name: str = Field(..., examples=["Beta-thalassemia"])
    parent1_status: CarrierStatus
    parent2_status: CarrierStatus
    inheritance_mode: InheritanceMode = InheritanceMode.AUTOSOMAL_RECESSIVE
    relationship_type: Optional[str] = Field(
        None,
        description="Contextual only, does not affect the calculation itself "
                    "-- e.g. 'first_cousin', 'second_cousin', 'unrelated'.",
        examples=["first_cousin"],
    )


class ConsanguinityResponse(BaseModel):
    condition_name: str
    inheritance_mode: str
    relationship_type: Optional[str]
    probabilities: dict
    explanation: str


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/assess",
    response_model=ConsanguinityResponse,
    summary="Calculate offspring risk from two parents' known carrier status",
)
def assess_consanguinity_risk(payload: ConsanguinityRequest):
    """
    Direct risk calculator -- does not require an existing family tree.
    For inferring risk FROM a family history instead of stated carrier
    status, use the family-history module's /analyze endpoint, which shares
    this same underlying engine.
    """
    probabilities = punnett_square(
        payload.parent1_status,
        payload.parent2_status,
        payload.inheritance_mode,
    )

    explanation = _build_explanation(
        payload.condition_name,
        payload.parent1_status,
        payload.parent2_status,
        payload.inheritance_mode,
        probabilities,
        payload.relationship_type,
    )

    return ConsanguinityResponse(
        condition_name=payload.condition_name,
        inheritance_mode=payload.inheritance_mode.value,
        relationship_type=payload.relationship_type,
        probabilities=probabilities,
        explanation=explanation,
    )


def _build_explanation(
    condition: str,
    p1: CarrierStatus,
    p2: CarrierStatus,
    mode: InheritanceMode,
    probs: dict,
    relationship_type: Optional[str],
) -> str:
    """
    Plain-language summary. This is a template placeholder -- swap for a call
    to the shared AI-explanation service (Anthropic API) once that layer is
    wired in, passing this same structured data as context.
    """
    affected_pct = round(probs.get("affected", 0) * 100)
    carrier_pct = round(probs.get("carrier", 0) * 100)
    unaffected_pct = round(probs.get("unaffected", 0) * 100)

    lines = [
        f"Based on the stated carrier status for {condition} "
        f"({p1.value} and {p2.value}, {mode.value.replace('_', ' ')} inheritance), "
        f"each pregnancy has an estimated {affected_pct}% chance of an affected child, "
        f"{carrier_pct}% chance of an unaffected carrier, and "
        f"{unaffected_pct}% chance of an unaffected, non-carrier child."
    ]
    if relationship_type and relationship_type != "unrelated":
        lines.append(
            f"Note: a '{relationship_type}' relationship does not change these "
            "probabilities directly, but related couples are statistically more "
            "likely to both carry the same rare variant, which is why carrier "
            "testing is often recommended in this situation."
        )
    lines.append(
        "This is a decision-support estimate, not a diagnosis. Please discuss "
        "these results with a genetic counselor."
    )
    return " ".join(lines)