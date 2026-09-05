from typing import Dict


def align_effect_allele(match: Dict) -> Dict:
    """
    Determine the effect-allele dosage from a matched VCF variant.

    The PGS model defines:
        effect_allele
        other_allele

    The VCF provides:
        REF
        ALT
        GT

    For this first implementation, we require the VCF REF/ALT
    to exactly match the PGS other/effect allele orientation.
    """

    vcf_variant = match.get("vcf_variant")

    if not vcf_variant:
        return {
            **match,
            "alignment_status": "NOT_FOUND",
        }

    ref = vcf_variant["ref"].upper()
    alt = vcf_variant["alt"].upper()

    effect = match["effect_allele"].upper()
    other = match["other_allele"].upper()

    if ref == other and alt == effect:
        alignment_status = "ALIGNED"

    elif ref == effect and alt == other:
        alignment_status = "REVERSED"

    else:
        alignment_status = "ALLELE_MISMATCH"

    return {
        **match,
        "alignment_status": alignment_status,
    }


if __name__ == "__main__":

    from .vcf_parser import parse_vcf
    from .pgs_model import load_pgs_model
    from .variant_matcher import match_variants

    vcf = parse_vcf(
        "app/modules/wes_analysis/prs/synthetic.vcf"
    )

    pgs = load_pgs_model(
        "app/modules/wes_analysis/prs/models/PGS005336.txt.gz",
        max_variants=5,
    )

    matches = match_variants(
        vcf,
        pgs["variants"],
    )

    print("\nAllele alignment:")

    for match in matches:
        result = align_effect_allele(match)

        print(
            match["chrom"],
            match["pos"],
            "->",
            result["alignment_status"],
        )