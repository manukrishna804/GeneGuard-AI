from typing import Dict, List

from .dosage import genotype_to_dosage


def calculate_prs(matches: List[Dict]) -> Dict:
    """
    Calculate:

        PRS = sum(dosage * beta)

    Only MATCHED + ALIGNED variants are included.
    """

    contributions = []
    total_score = 0.0

    for match in matches:

        if match.get("status") != "MATCHED":
            continue

        if match.get("alignment_status") != "ALIGNED":
            continue

        vcf_variant = match["vcf_variant"]

        dosage = genotype_to_dosage(
            vcf_variant["genotype"]
        )

        beta = match["beta"]

        contribution = dosage * beta

        total_score += contribution

        contributions.append({
            "chrom": match["chrom"],
            "pos": match["pos"],
            "genotype": vcf_variant["genotype"],
            "dosage": dosage,
            "effect_allele": match["effect_allele"],
            "beta": beta,
            "contribution": contribution,
        })

    return {
        "prs": total_score,
        "contributions": contributions,
    }