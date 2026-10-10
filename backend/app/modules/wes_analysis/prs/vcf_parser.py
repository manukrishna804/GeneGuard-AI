from pathlib import Path
from typing import Dict, List, Optional, Iterable, Tuple
import subprocess


def _merge_positions(
    positions: Iterable[Tuple[str, int]],
    gap: int = 100_000,
) -> Dict[str, List[Tuple[int, int, set[int]]]]:
    """
    Merge nearby requested positions into genomic ranges.
    """

    grouped: Dict[str, List[int]] = {}

    for chrom, pos in positions:
        grouped.setdefault(str(chrom), []).append(int(pos))

    merged: Dict[str, List[Tuple[int, int, set[int]]]] = {}

    for chrom, pos_list in grouped.items():

        sorted_positions = sorted(set(pos_list))

        if not sorted_positions:
            continue

        ranges = []

        start = sorted_positions[0]
        end = sorted_positions[0]
        requested = {sorted_positions[0]}

        for pos in sorted_positions[1:]:

            if pos - end <= gap:
                end = pos
                requested.add(pos)

            else:
                ranges.append(
                    (start, end, requested)
                )

                start = pos
                end = pos
                requested = {pos}

        ranges.append(
            (start, end, requested)
        )

        merged[chrom] = ranges

    return merged


def _windows_to_wsl_path(path: Path) -> str:
    """
    Convert a Windows path such as:

        C:\\Users\\User\\file.vcf.gz

    into:

        /mnt/c/Users/User/file.vcf.gz
    """

    absolute_path = str(path.absolute()).replace("\\", "/")

    drive = absolute_path[0].lower()
    remaining = absolute_path[2:]

    return f"/mnt/{drive}{remaining}"


def _run_bcftools(
    command: List[str],
) -> subprocess.CompletedProcess:
    """
    Run bcftools through WSL.
    """

    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

    except FileNotFoundError as exc:
        raise RuntimeError(
            "WSL or bcftools not found."
        ) from exc

    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"bcftools failed:\n{exc.stderr}"
        ) from exc


def parse_vcf(
    vcf_path: str,
    sample_id: Optional[str] = None,
    positions: Optional[Iterable[Tuple[str, int]]] = None,
    rsids: Optional[Iterable[str]] = None,
) -> List[Dict]:
    """
    Parse a VCF/VCF.GZ using bcftools through WSL.

    Supports:

    1. Position-based lookup
       chromosome + position

    2. RS-ID-based lookup
       rsID

    Only requested variants are returned.
    """

    path = Path(vcf_path)

    if not path.exists():
        raise FileNotFoundError(
            f"VCF file not found: {vcf_path}"
        )

    if positions is None and rsids is None:
        raise ValueError(
            "positions or rsids must be provided."
        )

    if sample_id is None:
        raise ValueError(
            "sample_id is required."
        )

    requested_rsids = {
        str(rsid).strip()
        for rsid in (rsids or [])
        if str(rsid).strip()
    }

    variants: List[Dict] = []

    format_string = (
        "%CHROM\t%POS\t%ID\t%REF\t%ALT[\t%GT]\n"
    )

    vcf_wsl_path = _windows_to_wsl_path(path)

    # ---------------------------------------------------------
    # Position-based lookup
    # ---------------------------------------------------------

    if positions is not None:

        merged_ranges = _merge_positions(
            positions,
            gap=100_000,
        )

        for chrom, ranges in merged_ranges.items():

            for start, end, requested_positions in ranges:

                region = f"{chrom}:{start}-{end}"

                command = [
                    "wsl",
                    "bcftools",
                    "query",
                    "-s",
                    sample_id,
                    "-f",
                    format_string,
                    "-r",
                    region,
                    vcf_wsl_path,
                ]

                result = _run_bcftools(command)

                for line in result.stdout.splitlines():

                    if not line.strip():
                        continue

                    columns = line.split("\t")

                    if len(columns) < 6:
                        continue

                    chrom_value = columns[0]
                    pos = int(columns[1])

                    if (
                        chrom_value != chrom
                        or pos not in requested_positions
                    ):
                        continue

                    variants.append(
                        {
                            "chrom": chrom_value,
                            "pos": pos,
                            "id": columns[2],
                            "ref": columns[3],
                            "alt": columns[4],
                            "genotype": columns[5],
                        }
                    )

    # ---------------------------------------------------------
    # RS-ID-based lookup
    # ---------------------------------------------------------

    if requested_rsids:
        requested_rsids_list = sorted(requested_rsids)

        batch_size = 500

        for batch_start in range(
            0,
            len(requested_rsids_list),
            batch_size,
        ):
            batch = requested_rsids_list[
                batch_start:batch_start + batch_size
            ]

            expression = " || ".join(
                f'ID="{rsid}"'
                for rsid in batch
            )

            command = [
                "wsl",
                "bcftools",
                "query",
                "-s",
                sample_id,
                "-f",
                format_string,
                "-i",
                expression,
                vcf_wsl_path,
            ]

            result = _run_bcftools(command)

            for line in result.stdout.splitlines():
                fields = line.split("\t")

                if len(fields) < 6:
                    continue

                chrom = fields[0]
                pos = int(fields[1])
                variant_id = fields[2]
                ref = fields[3]
                alt = fields[4]
                genotype = fields[5]

                variants.append(
                    {
                        "chrom": chrom,
                        "pos": pos,
                        "id": variant_id,
                        "ref": ref,
                        "alt": alt,
                        "genotype": genotype,
                    }
                )

    variants.sort(
        key=lambda x: (
            x["chrom"],
            x["pos"],
        )
    )

    return variants


if __name__ == "__main__":

    vcf_path = (
        "app/modules/wes_analysis/prs/"
        "data/chr10_1000genomes.vcf.gz"
    )

    positions = [
        ("10", 100000625),
        ("10", 100004906),
        ("10", 100005282),
        ("10", 100007243),
        ("10", 100007626),
    ]

    variants = parse_vcf(
        vcf_path,
        sample_id="HG00096",
        positions=positions,
    )

    print(
        f"\nParsed {len(variants)} variants"
    )

    for variant in variants:
        print(variant)