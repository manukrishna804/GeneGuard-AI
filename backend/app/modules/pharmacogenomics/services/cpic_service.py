
from typing import Any, Dict, Optional

import httpx


# ============================================================
# CPIC / ClinPGx SERVICE
# ============================================================

CPIC_BASE_URL = "https://api.cpicpgx.org/v1"


class CPICService:
    """
    Retrieves pharmacogenomic recommendations from
    the ClinPGx recommendation_view endpoint.
    """

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    async def get_guideline(
        self,
        gene: str,
        drug: str,
        phenotype: Optional[str] = None,
        population: Optional[str] = None,
        guideline_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        result: Dict[str, Any] = {
            "gene": gene,
            "drug": drug,
            "guideline_id": guideline_id,
            "source": "CPIC",
            "available": False,
            "evidence_level": None,
            "recommendation": None,
            "implication": None,
            "guideline_version": None,
            "population": population,
            "raw_data": None,
            "multiple_recommendations": False,
        }

        # ----------------------------------------------------
        # Build ClinPGx API filters
        # ----------------------------------------------------

        params: Dict[str, str] = {
            "drugname": f"eq.{drug.strip().lower()}",
        }

        if phenotype:
            lookup_json = (
                f'{{"{gene.strip().upper()}":"{phenotype.strip()}"}}'
            )
            params["lookupkey"] = f"cs.{lookup_json}"

        if population:
            params["population"] = (
                f"ilike.*{population.strip()}*"
            )

        url = f"{CPIC_BASE_URL}/recommendation_view"

        # ----------------------------------------------------
        # Request API
        # ----------------------------------------------------

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.get(
                    url,
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

        except httpx.HTTPStatusError as exc:
            result["error"] = (
                f"ClinPGx returned HTTP {exc.response.status_code}"
            )
            return result

        except (httpx.RequestError, ValueError) as exc:
            result["error"] = str(exc)
            return result

        except Exception as exc:
            result["error"] = str(exc)
            return result

        if not isinstance(data, list) or not data:
            result["raw_data"] = data
            return result

        # ----------------------------------------------------
        # Verify returned records
        # ----------------------------------------------------

        gene_upper = gene.strip().upper()
        phenotype_normalized = (
            phenotype.strip().casefold()
            if phenotype else None
        )

        matching_records = []

        for item in data:
            lookupkey = item.get("lookupkey") or {}

            # Verify gene and phenotype if a phenotype
            # was requested.
            if phenotype_normalized:
                returned_phenotype = lookupkey.get(gene_upper)

                if (
                    not isinstance(returned_phenotype, str)
                    or returned_phenotype.strip().casefold()
                    != phenotype_normalized
                ):
                    continue

            # Verify population when specified.
            if population:
                returned_population = (
                    item.get("population") or ""
                ).strip().casefold()

                if returned_population != population.strip().casefold():
                    continue

            matching_records.append(item)

        result["raw_data"] = matching_records

        if not matching_records:
            result["error"] = (
                "No recommendation matched the requested "
                "drug, phenotype, and clinical indication."
            )
            return result

        # ----------------------------------------------------
        # Do not choose arbitrarily between clinical contexts
        # ----------------------------------------------------

        if not population and len(matching_records) > 1:
            result["available"] = True
            result["multiple_recommendations"] = True
            return result

        if len(matching_records) > 1:
            result["available"] = True
            result["multiple_recommendations"] = True
            result["error"] = (
                "Multiple recommendations matched. "
                "Additional clinical-context selection is required."
            )
            return result

        # Exactly one matching recommendation remains.
        recommendation = matching_records[0]

        result["available"] = True
        result["recommendation"] = (
            recommendation.get("drugrecommendation")
        )
        result["evidence_level"] = (
            recommendation.get("classification")
        )
        result["implication"] = (
            recommendation.get("implications")
        )
        result["guideline_id"] = (
            guideline_id
            or recommendation.get("guidelineurl")
        )
        result["guideline_version"] = (
            recommendation.get("guidelinename")
        )
        result["population"] = (
            recommendation.get("population")
        )

        return result


async def fetch_cpic_guideline(
    gene: str,
    drug: str,
    phenotype: Optional[str] = None,
    population: Optional[str] = None,
    guideline_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function used by the Module 5 pipeline.
    """

    service = CPICService()

    return await service.get_guideline(
        gene=gene,
        drug=drug,
        phenotype=phenotype,
        population=population,
        guideline_id=guideline_id,
    )
