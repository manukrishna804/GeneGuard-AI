from typing import Dict, List


def match_variants(
    vcf_variants: List[Dict],
    pgs_variants: List[Dict],
) -> List[Dict]:
    """
    Match PGS variants against patient VCF variants.

    Uses:
    1. RS ID when the PGS model provides one.
    2. Otherwise chromosome + position + REF + ALT.
    """

    vcf_by_rsid = {
        str(variant["id"]).strip(): variant
        for variant in vcf_variants
        if variant.get("id") and variant["id"] != "."
    }

    vcf_by_position = {
        (
            str(variant["chrom"]),
            int(variant["pos"]),
            str(variant["ref"]).upper(),
            str(variant["alt"]).upper(),
        ): variant
        for variant in vcf_variants
    }

    matches = []

    for pgs_variant in pgs_variants:

        rsid = str(
            pgs_variant.get("rsid", "")
        ).strip()

        patient_variant = None

        # RS-ID matching
        if rsid:
            patient_variant = vcf_by_rsid.get(rsid)

        # Position matching fallback
        if patient_variant is None and pgs_variant.get("pos") is not None:
            key = (
                str(pgs_variant["chrom"]),
                int(pgs_variant["pos"]),
                str(pgs_variant["other_allele"]).upper(),
                str(pgs_variant["effect_allele"]).upper(),
            )

            patient_variant = vcf_by_position.get(key)

        matches.append(
            {
                "chrom": pgs_variant["chrom"],
                "pos": pgs_variant.get("pos"),
                "rsid": rsid,
                "status": (
                    "MATCHED"
                    if patient_variant
                    else "NOT_FOUND"
                ),
                "vcf_variant": patient_variant,
                "effect_allele": pgs_variant["effect_allele"],
                "other_allele": pgs_variant.get(
                    "other_allele",
                    "",
                ),
                "beta": pgs_variant["beta"],
            }
        )

    return matches