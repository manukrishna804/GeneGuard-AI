from typing import Dict, List


def calculate_prs_qc(
    matches: List[Dict],
    total_model_variants: int,
) -> Dict:

    matched = sum(
        1
        for match in matches
        if match.get("status") == "MATCHED"
    )

    aligned = sum(
        1
        for match in matches
        if (
            match.get("status") == "MATCHED"
            and match.get("alignment_status") == "ALIGNED"
        )
    )

    missing = total_model_variants - matched

    coverage = (
        matched / total_model_variants
        if total_model_variants
        else 0.0
    )

    alignment_rate = (
        aligned / matched
        if matched
        else 0.0
    )

    if aligned == 0:
        status = "INSUFFICIENT_COVERAGE"

    elif coverage < 0.80:
        status = "PARTIAL_COVERAGE"

    else:
        status = "CALCULATED"

    return {
        "total_model_variants": total_model_variants,
        "matched_variants": matched,
        "aligned_variants": aligned,
        "missing_variants": missing,
        "coverage": coverage,
        "alignment_rate": alignment_rate,
        "status": status,
    }
if __name__ == "__main__":

    from .vcf_parser import parse_vcf
    from .pgs_model import load_pgs_model
    from .variant_matcher import match_variants

    vcf = parse_vcf(
        "app/modules/wes_analysis/prs/synthetic.vcf"
    )

    pgs = load_pgs_model(
        "app/modules/wes_analysis/prs/synthetic_pgs.tsv"
    )

    matches = match_variants(
        vcf,
        pgs,
    )

    result = calculate_prs_qc(
        matches,
        total_model_variants=len(pgs),
    )

    print("\nPRS QC:")
    print(result)