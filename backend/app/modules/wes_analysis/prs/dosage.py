from typing import Dict


def genotype_to_dosage(
    genotype: str,
    effect_allele_index: int = 1,
) -> int:
    """
    Convert a biallelic VCF genotype to effect-allele dosage.

    0/0 -> 0
    0/1 -> 1
    1/0 -> 1
    1/1 -> 2
    """

    if genotype in {"./.", ".", ".|."}:
        raise ValueError(f"Missing genotype: {genotype}")

    separator = "/" if "/" in genotype else "|"

    alleles = genotype.split(separator)

    if len(alleles) != 2:
        raise ValueError(
            f"Unsupported genotype format: {genotype}"
        )

    return sum(
        1
        for allele in alleles
        if int(allele) == effect_allele_index
    )


if __name__ == "__main__":

    test_genotypes = [
        "0/0",
        "0/1",
        "1/0",
        "1/1",
    ]

    print("\nGenotype dosage:")

    for genotype in test_genotypes:

        dosage = genotype_to_dosage(
            genotype
        )

        print(
            f"{genotype} -> {dosage}"
        )