from typing import Any, Dict, Optional

import httpx


CPIC_BASE_URL = "https://api.cpicpgx.org/v1"


class CPICService:

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

        result = {
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
        }

        # ---------------------------------------------
        # Build the same filters we tested in Swagger
        # ---------------------------------------------

        params = {
            "drugname": f"eq.{drug.lower()}",
        }

        if phenotype:
            params["lookupkey"] = (
                f'cs.{{"{gene}":"{phenotype}"}}'
            )

        if population:
            params["population"] = f"ilike.*{population}*"

        # ---------------------------------------------
        # Request ClinPGx
        # ---------------------------------------------

        url = f"{CPIC_BASE_URL}/recommendation_view"

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

        except Exception as exc:
            result["error"] = str(exc)
            return result

        # ---------------------------------------------
        # No recommendation found
        # ---------------------------------------------

        if not data:
            return result

        # ---------------------------------------------
        # Recommendation found
        # ---------------------------------------------

        result["available"] = True
        result["raw_data"] = data

        first = data[0]

        result["guideline_id"] = (
            guideline_id
            or first.get("guidelineurl")
        )

        result["recommendation"] = (
            first.get("drugrecommendation")
        )

        result["implication"] = (
            first.get("implications")
        )

        result["evidence_level"] = (
            first.get("classification")
        )

        result["guideline_version"] = (
            first.get("guidelinename")
        )

        result["population"] = (
            first.get("population")
        )

        return result


async def fetch_cpic_guideline(
    gene: str,
    drug: str,
    phenotype: Optional[str] = None,
    population: Optional[str] = None,
    guideline_id: Optional[str] = None,
) -> Dict[str, Any]:

    service = CPICService()

    return await service.get_guideline(
        gene=gene,
        drug=drug,
        phenotype=phenotype,
        population=population,
        guideline_id=guideline_id,
    )