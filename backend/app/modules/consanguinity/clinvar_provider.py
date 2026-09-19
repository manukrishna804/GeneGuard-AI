from __future__ import annotations

import json
from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .annotation_provider import AnnotationProvider
from .schemas import GeneticVariant, VariantClassification


def build_variant_identifier(
    variant: GeneticVariant,
) -> str | None:
    """
    Build a normalized genomic-coordinate identifier.

    Example:
        chr11:5227002:A:G
        becomes:
        11:5227002:A:G
    """

    if (
        not variant.chromosome
        or variant.position is None
        or not variant.reference
        or not variant.alternate
    ):
        return None

    chromosome = variant.chromosome

    if chromosome.lower().startswith("chr"):
        chromosome = chromosome[3:]

    return f"{chromosome}:{variant.position}:{variant.reference}:{variant.alternate}"


def search_clinvar_ids(
    variant: GeneticVariant,
    timeout: int = 10,
) -> list[str]:
    """
    Search ClinVar using the variant's genomic coordinate identifier.
    """

    identifier = build_variant_identifier(variant)

    if identifier is None:
        return []

    params = {
        "db": "clinvar",
        "term": identifier,
        "retmode": "json",
        "retmax": "10",
    }

    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
        + urlencode(params)
    )

    request = Request(
        url,
        headers={
            "User-Agent": "GeneGuard-AI/1.0",
        },
    )

    with urlopen(request, timeout=timeout) as response:
        data = json.loads(
            response.read().decode("utf-8")
        )

    return data.get(
        "esearchresult",
        {},
    ).get(
        "idlist",
        [],
    )


def fetch_clinvar_record(
    clinvar_id: str,
    timeout: int = 10,
) -> dict | None:
    """
    Fetch a ClinVar summary record by ClinVar Variation ID.
    """

    params = {
        "db": "clinvar",
        "id": clinvar_id,
        "retmode": "json",
    }

    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
        + urlencode(params)
    )

    request = Request(
        url,
        headers={
            "User-Agent": "GeneGuard-AI/1.0",
        },
    )

    with urlopen(request, timeout=timeout) as response:
        data = json.loads(
            response.read().decode("utf-8")
        )

    result = data.get("result", {})

    return result.get(clinvar_id)


def clinvar_record_to_variant(
    record: dict,
    original_variant: GeneticVariant,
) -> GeneticVariant:
    """
    Convert a ClinVar summary record into the project's
    standardized GeneticVariant model.
    """

    classification_map = {
        "Pathogenic": VariantClassification.PATHOGENIC,
        "Likely pathogenic": VariantClassification.LIKELY_PATHOGENIC,
        "Uncertain significance": VariantClassification.VUS,
        "Likely benign": VariantClassification.LIKELY_BENIGN,
        "Benign": VariantClassification.BENIGN,
    }

    classification_description = (
        record
        .get("germline_classification", {})
        .get("description", "unknown")
    )

    classification = classification_map.get(
        classification_description,
        VariantClassification.UNKNOWN,
    )

    genes = record.get("genes", [])

    gene = original_variant.gene

    # ---------------------------------------------------------
    # Determine gene
    # ---------------------------------------------------------

    if gene == "UNKNOWN":

        title = record.get("title", "")

        title_gene = None

        if "(" in title and ")" in title:
            title_gene = title.split("(")[1].split(")")[0]

        if title_gene:

            for gene_record in genes:

                symbol = gene_record.get("symbol")

                if symbol == title_gene:
                    gene = symbol
                    break

    # Fallback to the first available gene.
    if gene == "UNKNOWN":

        for gene_record in genes:

            symbol = gene_record.get("symbol")

            if symbol:
                gene = symbol
                break

    # ---------------------------------------------------------
    # Determine condition
    # ---------------------------------------------------------

    trait_set = (
        record
        .get("germline_classification", {})
        .get("trait_set", [])
    )

    condition = None

    for trait in trait_set:

        trait_name = trait.get("trait_name")

        if (
            trait_name
            and trait_name.lower() != "not provided"
        ):
            condition = trait_name
            break

    # ---------------------------------------------------------
    # Variant name
    # ---------------------------------------------------------

    variant_name = record.get("title")

    # ---------------------------------------------------------
    # Evidence
    # ---------------------------------------------------------

    evidence_sources = ["ClinVar"]

    accession = record.get("accession")

    if accession:
        evidence_sources.append(
            f"ClinVar:{accession}"
        )

    # ---------------------------------------------------------
    # Return standardized variant
    # ---------------------------------------------------------

    return original_variant.model_copy(
        update={
            "gene": gene,
            "variant_name": variant_name,
            "classification": classification,
            "condition": condition,
            "evidence_sources": evidence_sources,
        }
    )


class ClinVarProvider(AnnotationProvider):
    """
    ClinVar annotation provider.
    """

    def annotate(
        self,
        variant: GeneticVariant,
    ) -> Optional[GeneticVariant]:
        """
        Search ClinVar and annotate the variant.
        """

        clinvar_ids = search_clinvar_ids(variant)

        if not clinvar_ids:
            return None

        for clinvar_id in clinvar_ids:

            record = fetch_clinvar_record(clinvar_id)

            if record is None:
                continue

            return clinvar_record_to_variant(
                record,
                variant,
            )

        return None