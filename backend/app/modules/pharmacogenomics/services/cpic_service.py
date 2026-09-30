from typing import Any, Dict, Optional

import httpx


# ============================================================
# CPIC SERVICE
# ============================================================
#
# This service is responsible for retrieving CPIC guideline
# information.
#
# The rest of Module 5 should NOT need to know how the CPIC
# request is made.
#
# Later we can add:
#   - caching
#   - release/version tracking
#   - retries
#   - authentication if required
#   - more precise CPIC endpoint handling
# ============================================================


CPIC_BASE_URL = "https://cpicpgx.org"


class CPICService:
    """
    Client for CPIC guideline data.
    """

    def __init__(
        self,
        timeout: float = 10.0,
    ):
        self.timeout = timeout

    async def get_guideline(
        self,
        gene: str,
        drug: str,
        guideline_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve CPIC guideline information for a
        gene-drug combination.

        Parameters
        ----------
        gene:
            Pharmacogene name.

        drug:
            Medication name.

        guideline_id:
            Optional internal guideline identifier.

        Returns
        -------
        Dictionary containing the retrieved CPIC data
        or a structured unavailable response.
        """

        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        # We don't hard-code a fake clinical recommendation.
        #
        # The exact external CPIC endpoint/data format will
        # be connected here after we verify the current CPIC
        # data interface.
        # ----------------------------------------------------

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
            "raw_data": None,
        }

        return result


async def fetch_cpic_guideline(
    gene: str,
    drug: str,
    guideline_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function used by the Module 5 pipeline.
    """

    service = CPICService()

    return await service.get_guideline(
        gene=gene,
        drug=drug,
        guideline_id=guideline_id,
    )