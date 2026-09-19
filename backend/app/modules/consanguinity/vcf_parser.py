from __future__ import annotations

from pathlib import Path
from typing import List

from .schemas import GeneticVariant, Zygosity


def parse_vcf(file_path: str | Path) -> List[GeneticVariant]:
    """
    Parse a VCF file and extract basic variant information.

    This parser currently focuses on:
    - chromosome
    - position
    - reference allele
    - alternate allele
    - genotype / zygosity

    Annotation such as gene name, disease, ClinVar classification,
    and inheritance will be handled in later stages.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"VCF file not found: {file_path}")

    variants: List[GeneticVariant] = []

    sample_index = None
    format_index = None

    with file_path.open("r", encoding="utf-8") as file:

        for line in file:

            line = line.strip()

            # Ignore metadata/header lines
            if line.startswith("##"):
                continue

            # VCF column header
            if line.startswith("#CHROM"):
                columns = line.split("\t")

                if len(columns) > 9:
                    sample_index = 9

                continue

            # Ignore empty lines
            if not line:
                continue

            columns = line.split("\t")

            # Minimum VCF columns:
            # CHROM POS ID REF ALT QUAL FILTER INFO
            if len(columns) < 8:
                continue

            chromosome = columns[0]

            try:
                position = int(columns[1])
            except ValueError:
                # Invalid genomic position; skip this record
                continue

            reference = columns[3]
            alternate = columns[4]

            genotype = None

            # FORMAT + sample column
            if len(columns) >= 10:

                format_fields = columns[8].split(":")
                sample_fields = columns[9].split(":")

                if "GT" in format_fields:
                    gt_index = format_fields.index("GT")

                    if gt_index < len(sample_fields):
                        genotype = sample_fields[gt_index]

            zygosity = determine_zygosity(genotype)

            # 0/0 means the sample carries the reference allele
            # and therefore this record is not a variant for this sample.
            if genotype in {"0/0", "0|0"}:
                continue

            # Missing genotype should not be treated as a usable variant.
            if zygosity == Zygosity.UNKNOWN:
                continue

            variant = GeneticVariant(
                gene="UNKNOWN",
                chromosome=chromosome,
                position=position,
                reference=reference,
                alternate=alternate,
                variant_name=None,
                zygosity=zygosity,
            )

            variants.append(variant)

    return variants


def determine_zygosity(genotype: str | None) -> Zygosity:
    """
    Convert a VCF genotype into a simplified zygosity classification.
    """

    if not genotype:
        return Zygosity.UNKNOWN

    # VCF may use either '/' or '|'
    alleles = genotype.replace("|", "/").split("/")

    if len(alleles) != 2:
        return Zygosity.UNKNOWN

    allele1, allele2 = alleles

    if allele1 == "." or allele2 == ".":
        return Zygosity.UNKNOWN

    if allele1 == allele2:

        if allele1 == "0":
            return Zygosity.UNKNOWN

        return Zygosity.HOMOZYGOUS

    return Zygosity.HETEROZYGOUS