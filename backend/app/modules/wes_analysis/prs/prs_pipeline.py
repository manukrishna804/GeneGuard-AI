from typing import Dict, List, Optional
import json
from pathlib import Path

from .prs_score import prs_to_score_100
from .vcf_parser import parse_vcf
from .model_cache import get_prs_model
from .variant_matcher import match_variants
from .allele_aligner import align_effect_allele
from .prs_calculator import calculate_prs
from .prs_qc import calculate_prs_qc


REFERENCE_PATH = Path(
    "app/modules/wes_analysis/prs/data/reference_scores.json"
)
_REFERENCE_CACHE = None


def get_reference_data() -> dict:
    global _REFERENCE_CACHE

    if _REFERENCE_CACHE is None:
        if not REFERENCE_PATH.exists():
            raise FileNotFoundError(
                f"PRS reference file not found: {REFERENCE_PATH}"
            )

        with REFERENCE_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:
            _REFERENCE_CACHE = json.load(file)

    return _REFERENCE_CACHE


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
    Run the PRS pipeline for one disease.

    The PGS model is loaded from the in-memory model cache.
    The cached model is selected using the disease name.

    chromosomes:
        Optional chromosomes to include.

    max_variants:
        Optional development/test limit.
    """

    # --------------------------------------------------
    # 1. Load cached PGS model
    # --------------------------------------------------

    pgs_result = get_prs_model(
        disease
    )

    pgs_variants = list(
        pgs_result["variants"]
    )

    if not pgs_variants:
        raise ValueError(
            f"No variants loaded for {disease} PRS model."
        )

    # --------------------------------------------------
    # 2. Apply optional chromosome filter
    # --------------------------------------------------

    if chromosomes is not None:

        allowed_chromosomes = {
            str(chrom)
            for chrom in chromosomes
        }

        pgs_variants = [
            variant
            for variant in pgs_variants
            if str(
                variant.get("chrom", "")
            ) in allowed_chromosomes
        ]

    # --------------------------------------------------
    # 3. Apply optional variant limit
    # --------------------------------------------------

    if max_variants is not None:

        pgs_variants = pgs_variants[
            :max_variants
        ]

    if not pgs_variants:
        raise ValueError(
            f"No variants remain for {disease} "
            "after filtering."
        )

    # --------------------------------------------------
    # 4. Extract required variants from patient VCF
    # --------------------------------------------------

    if match_type == "rsid":

        rsids = [
            variant["rsid"]
            for variant in pgs_variants
            if variant.get("rsid")
        ]

        if not rsids:
            raise ValueError(
                f"{disease} model requires RS-ID matching, "
                "but no RSIDs were found."
            )

        vcf_variants = parse_vcf(
            vcf_path,
            sample_id=sample_id,
            rsids=rsids,
        )

    elif match_type == "position":

        positions = [
            (
                variant["chrom"],
                variant["pos"],
            )
            for variant in pgs_variants
            if variant.get("chrom")
            and variant.get("pos") is not None
        ]

        if not positions:
            raise ValueError(
                f"{disease} model requires position matching, "
                "but no genomic positions were found."
            )

        vcf_variants = parse_vcf(
            vcf_path,
            sample_id=sample_id,
            positions=positions,
        )

    else:

        raise ValueError(
            f"Unsupported PRS match type: {match_type}"
        )

    # --------------------------------------------------
    # 5. Match patient variants to PGS variants
    # --------------------------------------------------

    matches = match_variants(
        vcf_variants,
        pgs_variants,
    )

    # --------------------------------------------------
    # 6. Align effect alleles
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 7. Calculate raw PRS
    # --------------------------------------------------

    prs_result = calculate_prs(
        aligned_matches
    )

    # --------------------------------------------------
    # 8. Load reference distribution
    # --------------------------------------------------

    reference_data = get_reference_data()

    reference_scores = reference_data.get(disease)

    score_100 = None

    if reference_scores:
        score_100 = prs_to_score_100(
        prs_result["prs"],
        reference_scores,
    )

    # --------------------------------------------------
    # 10. Calculate QC
    # --------------------------------------------------

    qc_result = calculate_prs_qc(
        aligned_matches,
        total_model_variants=len(
            pgs_variants
        ),
    )

    # --------------------------------------------------
    # 11. Return result
    # --------------------------------------------------

    return {
        "disease": disease,
        "pgs_id": pgs_result["metadata"].get("pgs_id"),
        "model_name": pgs_result["metadata"].get("pgs_name"),
        "genome_build": pgs_result[
            "metadata"
        ].get("genome_build"),
        "prs": prs_result["prs"],
        "score_100": score_100,
        "score_100_status": "DEVELOPMENT_ONLY",
        "score_100_reference": "synthetic",
        "contributions": [],
        "qc": qc_result,
        "status": qc_result["status"],
    }


if __name__ == "__main__":

    result = run_prs_pipeline(
        vcf_path=(
            "app/modules/wes_analysis/prs/"
            "data/test/common_5_disease_test.vcf.gz"
        ),
        pgs_path=(
            "app/modules/wes_analysis/prs/models/"
            "PGS005336.txt.gz"
        ),
        disease="Type 2 diabetes",
        sample_id="HG00096",
        max_variants=5000,
        match_type="position",
    )

    print(
        "\nFinal PRS Pipeline Result:"
    )

    print(
        "PRS:",
        result["prs"],
    )

    print(
        "Score 100:",
        result["score_100"],
    )

    print(
        "QC:",
        result["qc"],
    )