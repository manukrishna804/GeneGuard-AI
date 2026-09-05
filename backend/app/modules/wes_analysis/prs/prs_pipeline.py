from typing import Dict, List, Optional
from .prs_score import prs_to_score_100
import json
from pathlib import Path

from .vcf_parser import parse_vcf
from .pgs_model import load_pgs_model
from .variant_matcher import match_variants
from .allele_aligner import align_effect_allele
from .prs_calculator import calculate_prs
from .prs_qc import calculate_prs_qc


def run_prs_pipeline(
    vcf_path: str,
    pgs_path: str,
    disease: str,
    sample_id: str,
    chromosomes: Optional[List[str]] = None,
    max_variants: Optional[int] = None,
    match_type: str = "position",
) -> Dict:
    """
    Run the PRS pipeline.

    chromosomes:
        Optional chromosomes to include, e.g. ["10"].

    max_variants:
        Optional limit for testing, e.g. 100.
    """

    # 1. Load PGS model
    pgs_result = load_pgs_model(
        pgs_path,
        chromosomes=chromosomes,
        max_variants=max_variants,
    )

    pgs_variants = pgs_result["variants"]

    # 2. Extract required genomic positions
    match_type = pgs_result["metadata"].get("match_type", "position")

    if match_type == "rsid":
        rsids = [
            variant["rsid"]
            for variant in pgs_variants
            if variant.get("rsid")
        ]

        vcf_variants = parse_vcf(
            vcf_path,
            sample_id=sample_id,
            rsids=rsids or None,
        )
    else:
        positions = [
            (variant["chrom"], variant["pos"])
            for variant in pgs_variants
            if variant.get("pos") is not None
        ]

    vcf_variants = parse_vcf(
        vcf_path,
        sample_id=sample_id,
        positions=positions or None,
    )

    # 4. Match variants
    matches = match_variants(
        vcf_variants,
        pgs_variants,
    )

    # 5. Align effect alleles
    aligned_matches = [
        align_effect_allele(match)
        for match in matches
    ]
    matched_count = sum(
    1
    for match in aligned_matches
    if match.get("status") == "MATCHED"
)

    if matched_count == 0:
        raise ValueError(
            f"No variants from {disease} PRS model "
            "were found in the uploaded VCF."
        )

    # 6. Calculate PRS
    prs_result = calculate_prs(
        aligned_matches
    )
    reference_path = Path(
        "app/modules/wes_analysis/prs/data/reference_scores.json"
    )

    with reference_path.open("r", encoding="utf-8") as f:
        reference_data = json.load(f)

    reference_scores = reference_data[disease]

    score_100 = prs_to_score_100(
        prs_result["prs"],
        reference_scores,
    )

    # 7. QC
    qc_result = calculate_prs_qc(
        aligned_matches,
        total_model_variants=len(pgs_variants),
    )

    return {
        "disease": disease,
        "sample_id": sample_id,
        "pgs_id": pgs_result["metadata"].get("pgs_id"),
        "model_name": pgs_result["metadata"].get("pgs_name"),
        "genome_build": pgs_result["metadata"].get(
            "genome_build"
        ),
        "prs": prs_result["prs"],
        "score_100": score_100,
        "contributions": prs_result["contributions"],
        "qc": qc_result,
        "status": qc_result["status"],
    }


if __name__ == "__main__":

    result = run_prs_pipeline(
        vcf_path=(
            "app/modules/wes_analysis/prs/"
            "data/chr10_1000genomes.vcf.gz"
        ),
        pgs_path=(
            "app/modules/wes_analysis/prs/models/"
            "PGS005336.txt.gz"
        ),
        disease="Type 2 diabetes",
        sample_id="HG00096",

        # Current test configuration
        chromosomes=["10"],
        max_variants=5000,
    )

    print("\nFinal PRS Pipeline Result:")
    print("PRS:", result["prs"])
    print("Score 100:", result["score_100"])
    print("QC:", result["qc"])