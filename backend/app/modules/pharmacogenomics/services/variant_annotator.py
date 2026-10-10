
from typing import Any

import requests


MYVARIANT_URL = "https://myvariant.info/v1/variant/"
MYVARIANT_QUERY_URL = "https://myvariant.info/v1/query"
REQUEST_TIMEOUT_SECONDS = 15


def _extract_gene(data: dict[str, Any]) -> str | None:
    dbnsfp = data.get("dbnsfp") or {}
    clinvar = data.get("clinvar") or {}
    gene_info = clinvar.get("gene") or {}

    gene_names = dbnsfp.get("genename")

    if isinstance(gene_names, list) and gene_names:
        return gene_names[0]

    if isinstance(gene_names, str):
        return gene_names

    return gene_info.get("symbol")


def _lookup_by_rsid(
    rsid: str,
    chromosome: str,
    position: int,
    reference: str,
    alternate: str,
) -> dict[str, Any]:
    """Search by rsID and accept only a matching allele record."""

    response = requests.get(
        MYVARIANT_QUERY_URL,
        params={
            "q": rsid,
            "fields": (
                "dbsnp.rsid,dbnsfp.genename,"
                "clinvar.gene.symbol,clinvar.alt,"
                "clinvar.hg38,clinvar.hgvs.genomic"
            ),
            "size": 20,
        },
        headers={"Accept": "application/json"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    results = response.json()

    for hit in results.get("hits", []):
        clinvar = hit.get("clinvar") or {}
        hg38 = clinvar.get("hg38") or {}
        genomic_ids = clinvar.get("hgvs", {}).get("genomic", [])

        if isinstance(genomic_ids, str):
            genomic_ids = [genomic_ids]

        expected_hgvs = (
            f"g.{position}{reference}>{alternate}"
        )

        exact_position = (
            hg38.get("start") == position
            and hg38.get("end") == position
        )
        exact_alternate = clinvar.get("alt") == alternate
        exact_reference_allele = any(
            expected_hgvs in genomic_id
            for genomic_id in genomic_ids
        )

        if (
            exact_position
            and exact_alternate
            and exact_reference_allele
        ):
            gene = _extract_gene(hit)

            return {
                "status": "success",
                "assembly": "GRCh38",
                "chromosome": chromosome,
                "position": position,
                "reference": reference,
                "alternate": alternate,
                "gene": gene,
                "rsid": rsid,
                "query": expected_hgvs,
                "annotation_source": "MyVariant.info",
            }

    return {
        "status": "not_found",
        "message": "No exact matching variant annotation was found.",
    }


def annotate_variant(
    chromosome: str,
    position: int,
    reference: str,
    alternate: str,
    rsid: str | None = None,
) -> dict[str, Any]:
    """
    Look up a variant using GRCh38 coordinates.

    Annotation does not assign star alleles or determine
    a patient's drug response.
    """
    if (
        not chromosome
        or position < 1
        or not reference
        or not alternate
    ):
        return {
            "status": "error",
            "message": (
                "Valid chromosome, position, reference "
                "and alternate are required."
            ),
        }

    chrom = chromosome.removeprefix("chr")
    genomic_hgvs = f"{chrom}:g.{position}{reference}>{alternate}"

    try:
        response = requests.get(
            f"{MYVARIANT_URL}{genomic_hgvs}",
            params={"assembly": "hg38"},
            headers={"Accept": "application/json"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        if response.status_code == 404:
            if rsid and rsid.startswith("rs"):
                return _lookup_by_rsid(
                    rsid=rsid,
                    chromosome=chrom,
                    position=position,
                    reference=reference,
                    alternate=alternate,
                )

            return {
                "status": "not_found",
                "message": "No annotation record was found for this variant.",
            }

        response.raise_for_status()
        data = response.json()
        gene = _extract_gene(data)

        return {
            "status": "success",
            "assembly": "GRCh38",
            "chromosome": chrom,
            "position": position,
            "reference": reference,
            "alternate": alternate,
            "gene": gene,
            "query": genomic_hgvs,
            "annotation_source": "MyVariant.info",
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Variant annotation service timed out.",
        }
    except requests.exceptions.RequestException:
        return {
            "status": "error",
            "message": "Variant annotation service is unavailable.",
        }
    except (ValueError, TypeError):
        return {
            "status": "error",
            "message": "Variant annotation service returned invalid data.",
        }


def annotate_parsed_variant(
    variant: dict[str, Any],
) -> dict[str, Any]:
    """Annotate a dictionary returned by the VCF parser."""
    return annotate_variant(
        chromosome=str(variant["chromosome"]),
        position=int(variant["position"]),
        reference=str(variant["reference"]),
        alternate=str(variant["alternate"]),
        rsid=variant.get("rsid"),
    )
