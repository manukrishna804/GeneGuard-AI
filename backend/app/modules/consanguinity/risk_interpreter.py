from __future__ import annotations

from .schemas import VariantRiskResult


def interpret_variant_risk(
    risk: VariantRiskResult,
) -> str:
    """
    Generate a concise explanation of a calculated
    Mendelian offspring-risk result.

    This is an explanatory layer only. It does not
    perform the probability calculation.
    """

    parent1 = risk.parent1_status
    parent2 = risk.parent2_status

    affected = risk.affected_probability
    carrier = risk.carrier_probability
    unaffected = risk.unaffected_probability

    condition = risk.condition or "the associated condition"
    inheritance = risk.inheritance or "unknown inheritance"

    affected_percent = affected * 100
    carrier_percent = carrier * 100
    unaffected_percent = unaffected * 100

    explanation = (
        f"The assessment concerns {condition}, "
        f"using an {inheritance} inheritance model. "
        f"Parent 1 is classified as {parent1} and "
        f"Parent 2 as {parent2}. "
        f"Under the current Mendelian model, the calculated "
        f"offspring probabilities are "
        f"{affected_percent:.1f}% affected, "
        f"{carrier_percent:.1f}% carrier, and "
        f"{unaffected_percent:.1f}% unaffected."
    )

    return explanation