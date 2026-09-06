from typing import Dict


def align_effect_allele(match: Dict) -> Dict:
    """
    Determine the effect-allele dosage from a matched VCF variant.

    The PGS model always provides:
        effect_allele

    Some PGS files also provide:
        other_allele

    The VCF provides:
        REF
        ALT
        GT

    Alignment rules:

    1. If PGS other_allele is available:
       REF == other_allele and ALT == effect_allele
           -> ALIGNED

       REF == effect_allele and ALT == other_allele
           -> REVERSED

    2. If PGS other_allele is unavailable:
       ALT == effect_allele
           -> ALIGNED

       REF == effect_allele
           -> REVERSED

    Otherwise:
        ALLELE_MISMATCH
    """

    vcf_variant = match.get("vcf_variant")

    if not vcf_variant:
        return {
            **match,
            "alignment_status": "NOT_FOUND",
        }

    ref = str(
        vcf_variant.get("ref", "")
    ).upper()

    alt = str(
        vcf_variant.get("alt", "")
    ).upper()

    effect = str(
        match.get("effect_allele", "")
    ).upper()

    other = str(
        match.get("other_allele", "")
    ).upper()

    if not effect:
        return {
            **match,
            "alignment_status": "ALLELE_MISMATCH",
        }

    # --------------------------------------------------
    # Models with an explicit other allele
    # --------------------------------------------------

    if other:

        if ref == other and alt == effect:
            alignment_status = "ALIGNED"

        elif ref == effect and alt == other:
            alignment_status = "REVERSED"

        else:
            alignment_status = "ALLELE_MISMATCH"

    # --------------------------------------------------
    # RS-ID-only models without other_allele
    # --------------------------------------------------

    else:

        if alt == effect:
            alignment_status = "ALIGNED"

        elif ref == effect:
            alignment_status = "REVERSED"

        else:
            alignment_status = "ALLELE_MISMATCH"

    return {
        **match,
        "alignment_status": alignment_status,
    }