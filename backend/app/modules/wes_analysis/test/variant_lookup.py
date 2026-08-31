"""
services/variant_lookup.py
============================
Multi-database variant evidence lookup for Module 1.

Queries ClinVar (clinical significance) and gnomAD (population frequency)
for a single variant, and returns a clean, consistent result -- explicitly
distinguishing "not found" (queried, no data exists) from an actual error
(network/API failure), so downstream code (report generation, AI
explanation) never has to guess which happened.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import requests


class LookupStatus(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"     # queried successfully, no data exists
    ERROR = "error"              # query itself failed (network, bad response, etc.)


@dataclass
class ClinVarResult:
    status: LookupStatus
    clinvar_ids: list
    raw_count: int
    error_message: Optional[str] = None


@dataclass
class GnomadResult:
    status: LookupStatus
    genome_af: Optional[float] = None
    exome_af: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class VariantEvidence:
    gene: str
    variant_notation: str
    clinvar: ClinVarResult
    gnomad: GnomadResult

    def is_novel(self) -> bool:
        """True if neither database has any record of this variant at all."""
        return (
            self.clinvar.status == LookupStatus.NOT_FOUND
            and self.gnomad.status == LookupStatus.NOT_FOUND
        )

    def to_dict(self) -> dict:
        return {
            "gene": self.gene,
            "variant_notation": self.variant_notation,
            "clinvar_status": self.clinvar.status.value,
            "gnomad_status": self.gnomad.status.value,
            "is_novel": self.is_novel(),
        }


def _search_clinvar(gene: str, mutation: str) -> ClinVarResult:
    try:
        term = f"{gene}[gene] AND {mutation}[Variant name]"
        resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "clinvar", "term": term, "retmax": 5, "retmode": "json"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()["esearchresult"]
        count = int(data.get("count", 0))
        ids = data.get("idlist", [])

        if count == 0:
            return ClinVarResult(status=LookupStatus.NOT_FOUND, clinvar_ids=[], raw_count=0)
        return ClinVarResult(status=LookupStatus.FOUND, clinvar_ids=ids, raw_count=count)

    except (requests.RequestException, KeyError, ValueError) as e:
        return ClinVarResult(
            status=LookupStatus.ERROR, clinvar_ids=[], raw_count=0,
            error_message=str(e),
        )


def _query_gnomad(chrom: str, pos: str, ref: str, alt: str) -> GnomadResult:
    try:
        variant_id = f"{chrom}-{pos}-{ref}-{alt}"
        query = """
        query VariantQuery($variantId: String!) {
          variant(variantId: $variantId, dataset: gnomad_r4) {
            variantId
            genome { af }
            exome { af }
          }
        }
        """
        resp = requests.post(
            "https://gnomad.broadinstitute.org/api",
            json={"query": query, "variables": {"variantId": variant_id}},
            timeout=10,
        )
        resp.raise_for_status()
        payload = resp.json()

        if payload.get("errors"):
            msg = payload["errors"][0].get("message", "")
            if "not found" in msg.lower():
                return GnomadResult(status=LookupStatus.NOT_FOUND)
            return GnomadResult(status=LookupStatus.ERROR, error_message=msg)

        variant = payload.get("data", {}).get("variant")
        if variant is None:
            return GnomadResult(status=LookupStatus.NOT_FOUND)

        genome = variant.get("genome") or {}
        exome = variant.get("exome") or {}
        return GnomadResult(
            status=LookupStatus.FOUND,
            genome_af=genome.get("af"),
            exome_af=exome.get("af"),
        )

    except (requests.RequestException, KeyError, ValueError) as e:
        return GnomadResult(status=LookupStatus.ERROR, error_message=str(e))


def get_variant_evidence(
    gene: str,
    mutation: str,
    chrom: Optional[str] = None,
    pos: Optional[str] = None,
    ref: Optional[str] = None,
    alt: Optional[str] = None,
) -> VariantEvidence:
    """
    Look up a single variant against ClinVar and (if genomic coordinates are
    supplied) gnomAD. Coordinates are optional because a report may only give
    HGVS notation -- in that case gnomAD is skipped and marked NOT_FOUND
    (since it cannot be queried without coordinates, not because we know it's
    absent from the database).
    """
    clinvar_result = _search_clinvar(gene, mutation)

    if chrom and pos and ref and alt:
        gnomad_result = _query_gnomad(chrom, pos, ref, alt)
    else:
        gnomad_result = GnomadResult(status=LookupStatus.NOT_FOUND,
                                      error_message="No genomic coordinates supplied")

    return VariantEvidence(
        gene=gene,
        variant_notation=mutation,
        clinvar=clinvar_result,
        gnomad=gnomad_result,
    )