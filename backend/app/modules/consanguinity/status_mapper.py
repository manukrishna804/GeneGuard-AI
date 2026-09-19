from __future__ import annotations

from .genetics_engine import CarrierStatus
from .schemas import Zygosity


def zygosity_to_ar_status(zygosity: Zygosity) -> CarrierStatus:
    """
    Map zygosity to a simplified carrier status for an
    autosomal-recessive variant.

    This is only a preliminary mapping.

    Heterozygous  -> Carrier
    Homozygous    -> Affected
    Unknown       -> Unknown
    Hemizygous    -> Unknown
    """

    if zygosity == Zygosity.HETEROZYGOUS:
        return CarrierStatus.CARRIER

    if zygosity == Zygosity.HOMOZYGOUS:
        return CarrierStatus.AFFECTED

    return CarrierStatus.UNKNOWN