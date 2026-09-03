from typing import Any, Dict, Optional

import requests


GNOMAD_API_URL = "https://gnomad.broadinstitute.org/api"


def get_gnomad_variant(
    chromosome: str,
    position: int,
    reference: str,
    alternate: str,
) -> Dict[str, Any]:
    """
    Query gnomAD for a GRCh38 SNV.

    This function retrieves population-frequency evidence only.
    It does not assign an ACMG criterion or clinical classification.
    """

    chromosome = str(chromosome).replace("chr", "")
    variant_id = f"{chromosome}-{int(position)}-{reference}-{alternate}"

    query = """
    query Variant($variantId: String!, $datasetId: DatasetId!) {
        variant(
            variantId: $variantId
            dataset: $datasetId
        ) {
            variant_id
            genome {
                ac
                an
                af
                homozygote_count
            }
        }
    }
    """

    variables = {
        "variantId": variant_id,
        "datasetId": "gnomad_r4"
    }

    try:
        response = requests.post(
            GNOMAD_API_URL,
            json={
                "query": query,
                "variables": variables,
            },
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

    except requests.Timeout:
        return {
            "status": "unavailable",
            "variant_id": variant_id,
            "reason": "gnomAD request timed out.",
        }

    except requests.RequestException as exc:
        return {
            "status": "unavailable",
            "variant_id": variant_id,
            "reason": "gnomAD request failed.",
            "error": str(exc),
        }

    except ValueError:
        return {
            "status": "unavailable",
            "variant_id": variant_id,
            "reason": "gnomAD returned invalid JSON.",
        }

    if payload.get("errors"):
        errors = payload["errors"]

        error_messages = [
            str(error.get("message", "")).lower()
            for error in errors
            if isinstance(error, dict)
    ]

    if any("variant not found" in message for message in error_messages):
        return {
            "status": "not_found",
            "variant_id": variant_id,
            "found": False,
        }

    return {
        "status": "unavailable",
        "variant_id": variant_id,
        "reason": "gnomAD GraphQL returned an error.",
        "error": errors
    }

    data = payload.get("data") or {}
    variant = data.get("variant")

    if not variant:
        return {
            "status": "not_found",
            "variant_id": variant_id,
            "found": False,
        }

    genome = variant.get("genome") or {}

    return {
        "status": "found",
        "found": True,
        "variant_id": variant.get("variant_id"),
        "allele_count": genome.get("ac"),
        "allele_number": genome.get("an"),
        "allele_frequency": genome.get("af"),
        "homozygote_count": genome.get("homozygote_count"),
    }


def evaluate_population_evidence(
    chromosome: Optional[str],
    position: Optional[int],
    reference: Optional[str],
    alternate: Optional[str],
) -> Dict[str, Any]:
    """
    Produce normalized population-frequency evidence.

    No ACMG classification is assigned here.
    """

    if not all([
        chromosome,
        position,
        reference,
        alternate,
    ]):
        return {
            "status": "unavailable",
            "reason": "Incomplete genomic variant coordinates."
        }

    return get_gnomad_variant(
        chromosome=chromosome,
        position=position,
        reference=reference,
        alternate=alternate,
    )