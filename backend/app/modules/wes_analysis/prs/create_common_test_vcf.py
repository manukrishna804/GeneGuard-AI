from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
import tempfile


BASE_DIR = Path("app/modules/wes_analysis/prs")
DATA_DIR = BASE_DIR / "data" / "test"

VCF_PATH = DATA_DIR / "common_5_disease_test.vcf.gz"
TBI_PATH = DATA_DIR / "common_5_disease_test.vcf.gz.tbi"

SAMPLE_ID = "HG00096"

MODELS = {
    "Type 2 diabetes": BASE_DIR / "models" / "PGS005336.txt.gz",
    "CAD": BASE_DIR / "models" / "PGS000019.txt.gz",
    "Hypertension": BASE_DIR / "models" / "PGS003020.txt.gz",
    "Alzheimer's disease": BASE_DIR / "models" / "PGS000025.txt.gz",
    "Breast Cancer": BASE_DIR / "models" / "PGS000004.txt.gz",
}


def windows_to_wsl_path(path: Path) -> str:
    """
    Convert a Windows path into a WSL /mnt/<drive>/... path.
    """

    absolute_path = str(path.absolute()).replace("\\", "/")

    drive = absolute_path[0].lower()
    remaining = absolute_path[2:]

    return f"/mnt/{drive}{remaining}"


def load_model_variants(
    path: Path,
    limit: int = 5000,
) -> List[dict]:
    """
    Load PGS variants using the same parser as the real PRS pipeline.

    This keeps the development VCF generator consistent with
    the production PRS model loader.
    """

    from app.modules.wes_analysis.prs.pgs_model import load_pgs_model

    result = load_pgs_model(
        str(path),
        max_variants=limit,
    )

    variants = []

    for variant in result["variants"]:
        variants.append(
            {
                "rsID": variant.get("rsid", ""),
                "chr_name": variant.get("chrom", ""),
                "chr_position": (
                    ""
                    if variant.get("pos") is None
                    else str(variant["pos"])
                ),
                "effect_allele": variant.get(
                    "effect_allele",
                    "",
                ),
                "other_allele": variant.get(
                    "other_allele",
                    "",
                ),
                "effect_weight": str(
                    variant.get("beta", "")
                ),
            }
        )

    return variants

def add_t2d_variants(
    variants: Dict[Tuple[str, int, str, str], dict],
) -> int:
    """
    Add position-based T2D variants.
    """

    records = load_model_variants(
        MODELS["Type 2 diabetes"],
        limit=5000,
    )

    added = 0

    for record in records:

        chrom = str(
            record.get("chr_name", "")
        ).strip()

        pos = str(
            record.get("chr_position", "")
        ).strip()

        ref = str(
            record.get("other_allele", "")
        ).strip().upper()

        alt = str(
            record.get("effect_allele", "")
        ).strip().upper()

        if not chrom or not pos or not ref or not alt:
            continue

        if not pos.isdigit():
            continue

        if ref not in {"A", "C", "G", "T"}:
            continue

        if alt not in {"A", "C", "G", "T"}:
            continue

        key = (
            chrom,
            int(pos),
            ref,
            alt,
        )

        variants[key] = {
            "chrom": chrom,
            "pos": int(pos),
            "id": ".",
            "ref": ref,
            "alt": alt,
        }

        added += 1

    return added


def add_rsid_variants(
    variants: Dict[Tuple[str, int, str, str], dict],
    disease: str,
) -> int:
    """
    Add RS-ID based variants for development testing.

    The RS-ID itself is the important value for the production
    matching path.

    Synthetic coordinates are assigned only because several
    downloaded PGS files do not provide chromosome/position.
    """

    records = load_model_variants(
        MODELS[disease],
        limit=5000,
    )

    added = 0

    for record in records:

        rsid = str(
            record.get("rsID", "")
        ).strip()

        if not rsid:
            continue

        chrom = str(
            record.get("chr_name", "")
        ).strip()

        if not chrom:
            chrom = "1"

        pos = str(
            record.get("chr_position", "")
        ).strip()

        if pos.isdigit():

            position = int(pos)

        else:

            # Development-only synthetic position.
            #
            # The PRS matcher uses rsID for these models,
            # so this coordinate is not used to establish
            # the biological identity of the variant.
            position = (
                1_000_000
                + abs(hash((disease, rsid)))
                % 500_000_000
            )

        effect = str(
            record.get("effect_allele", "A")
        ).strip().upper()

        if effect not in {
            "A",
            "C",
            "G",
            "T",
        }:
            effect = "A"

        other = {
            "A": "G",
            "G": "A",
            "C": "T",
            "T": "C",
        }[effect]

        key = (
            chrom,
            position,
            other,
            effect,
        )

        variants[key] = {
            "chrom": chrom,
            "pos": position,
            "id": rsid,
            "ref": other,
            "alt": effect,
        }

        added += 1

    return added


def write_vcf(
    variants: Dict[
        Tuple[str, int, str, str],
        dict,
    ],
) -> None:
    """
    Write, compress and index the common development VCF.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_vcf = (
            Path(temp_dir)
            / "common_5_disease_test.vcf"
        )

        # --------------------------------------------------
        # Write plain VCF
        # --------------------------------------------------

        with temp_vcf.open(
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                "##fileformat=VCFv4.2\n"
            )

            file.write(
                "##source=GeneGuardAI_PRSTest\n"
            )

            file.write(
                "##FORMAT=<ID=GT,"
                "Number=1,"
                "Type=String,"
                "Description=Genotype>\n"
            )

            file.write(
                "#CHROM\tPOS\tID\tREF\tALT\tQUAL\t"
                "FILTER\tINFO\tFORMAT\t"
                f"{SAMPLE_ID}\n"
            )

            sorted_variants = sorted(
                variants.values(),
                key=lambda x: (
                    str(x["chrom"]),
                    int(x["pos"]),
                ),
            )

            for variant in sorted_variants:

                file.write(
                    f"{variant['chrom']}\t"
                    f"{variant['pos']}\t"
                    f"{variant['id']}\t"
                    f"{variant['ref']}\t"
                    f"{variant['alt']}\t"
                    f".\t"
                    f"PASS\t"
                    f".\t"
                    f"GT\t"
                    f"1|1\n"
                )

        # --------------------------------------------------
        # Convert Windows path to WSL path
        # --------------------------------------------------

        temp_vcf_wsl = windows_to_wsl_path(
            temp_vcf
        )

        # --------------------------------------------------
        # bgzip
        # --------------------------------------------------

        subprocess.run(
            [
                "wsl",
                "bgzip",
                "-f",
                temp_vcf_wsl,
            ],
            check=True,
        )

        compressed_vcf = Path(
            str(temp_vcf) + ".gz"
        )

        # --------------------------------------------------
        # tabix
        # --------------------------------------------------

        compressed_vcf_wsl = (
            windows_to_wsl_path(
                compressed_vcf
            )
        )

        subprocess.run(
            [
                "wsl",
                "tabix",
                "-f",
                "-p",
                "vcf",
                compressed_vcf_wsl,
            ],
            check=True,
        )

        compressed_tbi = Path(
            str(compressed_vcf) + ".tbi"
        )

        # --------------------------------------------------
        # Copy files into project data directory
        # --------------------------------------------------

        windows_vcf = (
            DATA_DIR / VCF_PATH.name
        )

        windows_tbi = (
            DATA_DIR / TBI_PATH.name
        )

        windows_vcf.write_bytes(
            compressed_vcf.read_bytes()
        )

        windows_tbi.write_bytes(
            compressed_tbi.read_bytes()
        )
def main() -> None:
    variants: Dict[
        Tuple[str, int, str, str],
        dict,
    ] = {}

    # ------------------------------------------------------
    # Type 2 diabetes
    # ------------------------------------------------------

    t2d_count = add_t2d_variants(
        variants
    )

    counts = {
        "Type 2 diabetes": t2d_count,
    }

    # ------------------------------------------------------
    # CAD
    # ------------------------------------------------------

    counts["CAD"] = add_rsid_variants(
        variants,
        "CAD",
    )

    # ------------------------------------------------------
    # Hypertension
    # PGS003020: 24 position-based variants
    # ------------------------------------------------------

    hypertension_records = load_model_variants(
        MODELS["Hypertension"],
        limit=24,
    )

    hypertension_added = 0

    for record in hypertension_records:
        chrom = str(
            record.get("chr_name", "")
        ).strip()

        pos = str(
            record.get("chr_position", "")
        ).strip()

        effect = str(
            record.get("effect_allele", "")
        ).strip().upper()

        other = str(
            record.get("other_allele", "")
        ).strip().upper()

        if (
            not chrom
            or not pos.isdigit()
            or not effect
            or not other
        ):
            continue

        key = (
            chrom,
            int(pos),
            other,
            effect,
        )

        variants[key] = {
            "chrom": chrom,
            "pos": int(pos),
            "id": ".",
            "ref": other,
            "alt": effect,
        }

        hypertension_added += 1

    counts["Hypertension"] = hypertension_added

    # ------------------------------------------------------
    # Alzheimer's disease
    # ------------------------------------------------------

    counts["Alzheimer's disease"] = add_rsid_variants(
        variants,
        "Alzheimer's disease",
    )

    # ------------------------------------------------------
    # Breast Cancer
    # PGS000004: 313 position-based variants
    # ------------------------------------------------------

    breast_records = load_model_variants(
        MODELS["Breast Cancer"],
        limit=313,
    )

    breast_added = 0

    for record in breast_records:
        chrom = str(
            record.get("chr_name", "")
        ).strip()

        pos = str(
            record.get("chr_position", "")
        ).strip()

        effect = str(
            record.get("effect_allele", "")
        ).strip().upper()

        other = str(
            record.get("other_allele", "")
        ).strip().upper()

        if (
            not chrom
            or not pos.isdigit()
            or not effect
            or not other
        ):
            continue

        key = (
            chrom,
            int(pos),
            other,
            effect,
        )

        variants[key] = {
            "chrom": chrom,
            "pos": int(pos),
            "id": ".",
            "ref": other,
            "alt": effect,
        }

        breast_added += 1

    counts["Breast Cancer"] = breast_added

    # ------------------------------------------------------
    # Write VCF
    # ------------------------------------------------------

    write_vcf(
        variants
    )

    # ------------------------------------------------------
    # Summary
    # ------------------------------------------------------

    print(
        "Common test VCF created."
    )

    print(
        f"Total variants: {len(variants)}"
    )

    for disease, count in counts.items():
        print(
            f"{disease}: {count}"
        )

    print(
        f"VCF: {VCF_PATH}"
    )

    print(
        f"Index: {TBI_PATH}"
    )


if __name__ == "__main__":
    main()