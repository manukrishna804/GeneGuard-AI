import json
import os
from typing import Any, Dict, Optional

from groq import AsyncGroq


class AIExplainer:
    """
    AI explanation layer for Module 5.

    IMPORTANT:
    The AI does not make clinical decisions.

    It receives an already-generated rule-based
    recommendation and explains it in plain language.
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

        self.client: Optional[AsyncGroq] = None

        if self.api_key:
            self.client = AsyncGroq(
                api_key=self.api_key
            )

        self.model = os.getenv(
            "GROQ_MODEL",
            "llama-3.1-8b-instant",
        )

    async def explain(
        self,
        recommendation: Dict[str, Any],
    ) -> str:
        """
        Generate a patient-friendly explanation from
        structured evidence.

        The raw VCF is never sent to the LLM.
        """

        if not self.client:
            return self._fallback_explanation(
                recommendation
            )

        evidence_json = json.dumps(
            recommendation,
            indent=2,
            default=str,
        )

        prompt = f"""
You are the explanation layer of a pharmacogenomics
clinical decision-support system.

The clinical recommendation has ALREADY been produced
by a deterministic rule engine.

Your job is ONLY to explain that recommendation in
clear, simple language.

Do NOT:
- create a new recommendation
- change the recommendation
- override the rule engine
- invent clinical evidence
- invent guideline information
- make claims not present in the supplied evidence

If the evidence is incomplete or marked for review,
clearly mention that.

Use only the structured information supplied below.

STRUCTURED PHARMACOGENOMICS RESULT:

{evidence_json}

Write a concise explanation covering:

1. The relevant gene.
2. The patient's diplotype, if available.
3. The metabolizer phenotype, if available.
4. The medication involved.
5. What the existing recommendation says.
6. The evidence/source information available.
7. Any conflict or specialist-review warning.

Do not provide additional treatment options that are
not present in the supplied recommendation.
"""

        try:

            response = await self.client.chat.completions.create(
                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You explain structured "
                            "pharmacogenomics evidence. "
                            "You do not make clinical decisions."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],

                temperature=0.0,
            )

            explanation = (
                response.choices[0]
                .message
                .content
            )

            if explanation:
                return explanation.strip()

        except Exception:
            pass

        return self._fallback_explanation(
            recommendation
        )

    @staticmethod
    def _fallback_explanation(
        recommendation: Dict[str, Any],
    ) -> str:
        """
        Deterministic fallback explanation used when
        the AI service is unavailable.
        """

        gene = recommendation.get(
            "gene"
        )

        drug = recommendation.get(
            "drug"
        )

        diplotype = recommendation.get(
            "diplotype"
        )

        phenotype = recommendation.get(
            "phenotype"
        )

        recommendation_text = (
            recommendation.get(
                "recommendation"
            )
        )

        parts = []

        if gene:
            parts.append(
                f"The relevant pharmacogene is {gene}."
            )

        if diplotype:
            parts.append(
                f"The reported diplotype is {diplotype}."
            )

        if phenotype:
            parts.append(
                f"The associated phenotype is "
                f"{phenotype}."
            )

        if drug:
            parts.append(
                f"The medication being evaluated is "
                f"{drug}."
            )

        if recommendation_text:
            parts.append(
                f"The rule-based recommendation is: "
                f"{recommendation_text}."
            )

        if recommendation.get("conflict"):
            parts.append(
                "The evidence contains a conflict and "
                "requires specialist review."
            )

        if recommendation.get(
            "requires_review"
        ):
            parts.append(
                "Additional evidence review is "
                "recommended before finalization."
            )

        if not parts:
            return (
                "No sufficient structured information "
                "is available to generate an explanation."
            )

        return " ".join(parts)


async def explain_recommendation(
    recommendation: Dict[str, Any],
) -> str:
    """
    Convenience function for the Module 5 pipeline.
    """

    explainer = AIExplainer()

    return await explainer.explain(
        recommendation
    )