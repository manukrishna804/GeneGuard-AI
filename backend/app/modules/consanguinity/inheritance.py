from __future__ import annotations

from .genetics_engine import InheritanceMode


CONDITION_INHERITANCE = {
    "Hemoglobinopathy": InheritanceMode.AUTOSOMAL_RECESSIVE,
    "Cystic fibrosis": InheritanceMode.AUTOSOMAL_RECESSIVE,
}


def get_inheritance_mode(
    condition: str | None,
) -> InheritanceMode:
    """
    Determine the inheritance model for a known condition.

    This is a development mapping and should later be
    replaced or supplemented by authoritative annotation
    sources.
    """

    if not condition:
        return InheritanceMode.UNKNOWN

    return CONDITION_INHERITANCE.get(
        condition,
        InheritanceMode.UNKNOWN,
    )