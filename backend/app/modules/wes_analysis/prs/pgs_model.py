from pathlib import Path
from typing import Dict, List, Optional
import gzip


def _open_text_file(path: Path):
    """
    Open either a real gzip-compressed file or a plain-text file
    that may still have a .gz filename.
    """

    with path.open("rb") as raw_file:
        magic = raw_file.read(2)

    if magic == b"\x1f\x8b":
        return gzip.open(
            path,
            "rt",
            encoding="utf-8",
        )

    return path.open(
        "r",
        encoding="utf-8",
    )


def load_pgs_model(
    pgs_path: str,
    max_variants: Optional[int] = None,
    chromosomes: Optional[List[str]] = None,
) -> Dict:
    """
    Load a PGS Catalog scoring file.

    chromosomes:
        Optional list of chromosomes to keep, e.g. ["10"].
    """

    path = Path(pgs_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PGS scoring file not found: {pgs_path}"
        )

    metadata = {}
    variants = []

    if chromosomes is not None:
        chromosomes = {str(chrom) for chrom in chromosomes}

    with _open_text_file(path) as file:

        header = None

        for line in file:

            line = line.strip()

            if not line:
                continue

            # Metadata
            if line.startswith("#"):

                if "=" in line:

                    key, value = line.lstrip("#").split(
                        "=",
                        1,
                    )

                    metadata[key.strip()] = value.strip()

                continue

            # Scoring header
            if header is None:
                header = line.split("\t")
                continue

            values = line.split("\t")
            record = dict(zip(header, values))

            chrom = str(record.get("chr_name", "")).strip()

            # Chromosome filter
            if (
                chromosomes is not None
                and chrom not in chromosomes
            ):
                continue

            pos_value = record.get("chr_position", "").strip()

            variants.append(
                {
                    "rsid": record.get("rsID", "").strip(),
                    "chrom": chrom,
                    "pos": (
                        int(pos_value)
                        if pos_value.isdigit()
                        else None
                    ),
                    "effect_allele": record["effect_allele"].strip(),
                    "other_allele": record.get("other_allele", "").strip(),
                    "beta": float(record["effect_weight"]),
                }
            )

            if (
                max_variants is not None
                and len(variants) >= max_variants
            ):
                break

    return {
        "metadata": metadata,
        "variants": variants,
    }


if __name__ == "__main__":

    pgs_path = (
        "app/modules/wes_analysis/prs/models/"
        "PGS005336.txt.gz"
    )

    result = load_pgs_model(
        pgs_path,
        chromosomes=["10"],
        max_variants=5,
    )

    print("\nPGS Metadata:")

    for key, value in result["metadata"].items():
        print(f"{key} = {value}")

    print("\nFirst PGS variants:")

    for variant in result["variants"]:
        print(variant)