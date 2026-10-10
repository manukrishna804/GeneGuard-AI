
from pathlib import Path
from typing import Any, Dict, List


MAX_VCF_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


class VCFParseError(ValueError):
    """Raised when a VCF file cannot be parsed safely."""


def parse_vcf_content(content: bytes) -> List[Dict[str, Any]]:
    """
    Parse a VCF file into the VariantInput-compatible dictionaries
    expected by the existing Module 5 pipeline.

    This parser extracts basic variant records. It does NOT perform
    clinical variant interpretation, star-allele assignment, or
    validated diplotype calling.
    """

    if not content:
        raise VCFParseError("The uploaded VCF file is empty.")

    if len(content) > MAX_VCF_SIZE_BYTES:
        raise VCFParseError("The VCF file exceeds the 20 MB limit.")

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise VCFParseError(
            "The VCF file must be a valid text file."
        ) from exc

    variants: List[Dict[str, Any]] = []
    sample_column_index = None
    header_found = False

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()

        if not line or line.startswith("##"):
            continue

        if line.startswith("#CHROM"):
            columns = line.split("\t")

            if len(columns) < 8:
                raise VCFParseError(
                    f"Invalid VCF header on line {line_number}."
                )

            if len(columns) >= 10:
                sample_column_index = 9

            header_found = True
            continue

        if line.startswith("#"):
            continue

        if not header_found:
            raise VCFParseError(
                "The VCF file is missing its #CHROM header."
            )

        fields = line.split("\t")

        if len(fields) < 8:
            raise VCFParseError(
                f"Invalid VCF record on line {line_number}: "
                "expected at least 8 tab-separated columns."
            )

        chrom, pos, rsid, ref, alt, _qual, _filter, info = fields[:8]

        try:
            position = int(pos)
            if position < 1:
                raise ValueError
        except ValueError as exc:
            raise VCFParseError(
                f"Invalid genomic position on line {line_number}."
            ) from exc

        if not chrom or not ref or not alt:
            raise VCFParseError(
                f"Missing chromosome or allele on line {line_number}."
            )

        # Skip records that do not describe a concrete alternate allele.
        # Multiallelic records are split into separate ALT entries below.
        alternate_alleles = alt.split(",")

        genotype = None

        if sample_column_index is not None:
            if len(fields) <= sample_column_index:
                raise VCFParseError(
                    f"Missing sample genotype on line {line_number}."
                )

            format_fields = fields[8].split(":") if len(fields) > 8 else []
            sample_fields = fields[sample_column_index].split(":")

            if "GT" in format_fields:
                gt_index = format_fields.index("GT")
                if gt_index < len(sample_fields):
                    genotype = sample_fields[gt_index]

        for alternate in alternate_alleles:
            if (
                alternate == "."
                or alternate.startswith("<")
                or "[" in alternate
                or "]" in alternate
                or ref == "."
            ):
                continue

            # The parser deliberately leaves gene and star_allele unset.
            # A VCF rsID or position alone does not prove either value.
            variants.append(
                {
                    "chromosome": chrom,
                    "position": position,
                    "gene": None,
                    "reference": ref,
                    "alternate": alternate,
                    "genotype": genotype,
                    "rsid": (
                        rsid
                        if rsid and rsid != "."
                        else None
                    ),
                    "star_allele": None,
                }
            )

    if not header_found:
        raise VCFParseError(
            "No valid #CHROM header was found in the VCF file."
        )

    if not variants:
        raise VCFParseError(
            "No supported variant records were found in the VCF file."
        )

    return variants
