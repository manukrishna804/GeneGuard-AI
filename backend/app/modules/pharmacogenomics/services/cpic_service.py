from typing import Any, Dict, Optional

import httpx


# ============================================================
# CPIC / ClinPGx API
# ============================================================

CPIC_BASE_URL = "https://api.cpicpgx.org/v1"


class CPICService:
    """
    Client for retrieving CPIC/ClinPGx recommendations.
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
        }

        # ----------------------------------------------------
        # Build ClinPGx recommendation_view filters
        # ----------------------------------------------------

        params = {
            "drugname": f"eq.{drug.lower()}",
        }

        # JSON containment filter:
        #
        # {"CYP2C19": "Poor Metabolizer"}
        #
        # becomes:
        #
        # cs.{"CYP2C19":"Poor Metabolizer"}
        #
        if phenotype:
            lookup_json = (
                f'{{"{gene}":"{phenotype}"}}'
            )

            params["lookupkey"] = f"cs.{lookup_json}"

        # Guideline name is optional because not every caller
        # will have a guideline identifier.
        if gene and drug:
            params["guidelinename"] = (
                f"eq.{gene} and {gene} and {drug}"
            )

        # Population is optional because clinical context may
        # not always be available.
        #
        # Use ilike because the API data can contain trailing
        # whitespace, for example:
        #
        # "CVI ACS PCI "
        #
        if population:
            params["population"] = f"ilike.*{population}*"

        # ----------------------------------------------------
        # Make API request
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Process response
        # ----------------------------------------------------

        if not data:
            return result

        # ClinPGx may return multiple recommendations when
        # population is not specified.
        #
        # For now, we keep all returned records in raw_data.
        # The recommendation engine can decide how to handle
        # multiple clinical contexts.
        result["available"] = True
        result["raw_data"] = data

        # Use the first result for the simple fields.
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