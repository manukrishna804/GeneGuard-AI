
import json
import os
from typing import Any, Dict, Optional

from groq import AsyncGroq


class AIExplainer:
    """
    AI explanation layer for Module 5.

    The AI explains an existing recommendation and does not
    independently make clinical decisions.
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
        Generate a concise explanation from structured evidence.

        Raw VCF data is not sent to the LLM by this function.
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

An existing recommendation has already been generated.
Your task is to explain the supplied result, not to make
a new clinical decision.

Rules:
- Do not create or change a recommendation.
- Do not invent clinical evidence or guideline details.
- Do not describe a CPIC/ClinPGx recommendation as a
  local rule-based recommendation.
- Identify the recommendation source only when supported
  by the supplied structured result.
- If the evidence is incomplete or marked for review,
  state that clearly.
- Do not invent additional treatment options.
- Use simple, concise language.

STRUCTURED PHARMACOGENOMICS RESULT:

{evidence_json}

Explain:
1. The relevant gene.
2. The reported diplotype, if available.
3. The metabolizer phenotype, if available.
4. The medication being evaluated.
5. The supplied recommendation.
6. The evidence source and classification, if available.
7. Any conflict, warning, or need for further review.

Make clear that the result is clinical decision support
and should be reviewed by a qualified healthcare professional.
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Explain structured pharmacogenomics "
                            "results accurately. Do not make "
                            "independent clinical decisions."
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
                response.choices[0].message.content
            )

            if explanation and explanation.strip():
                return explanation.strip()

        except Exception:
            # Use the deterministic fallback if the AI service
            # fails. Do not expose internal API errors to patients.
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

        gene = recommendation.get("gene")
        drug = recommendation.get("drug")
        diplotype = recommendation.get("diplotype")
        phenotype = recommendation.get("phenotype")
        recommendation_text = recommendation.get(
            "recommendation"
        )
        source = recommendation.get("source")
        evidence_level = recommendation.get("evidence_level")

        evidence = recommendation.get("evidence") or {}
        cpic = evidence.get("cpic") or {}

        # Prefer the source recorded in the structured result.
        # Fall back to the nested CPIC evidence when needed.
        if not source and cpic.get("source"):
            source = cpic.get("source")

        if not evidence_level and cpic.get("evidence_level"):
            evidence_level = (
                f"CPIC {cpic['evidence_level']}"
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
                f"The associated phenotype is {phenotype}."
            )

        if drug:
            parts.append(
                f"The medication being evaluated is {drug}."
            )

        if recommendation_text:
            clean_recommendation = recommendation_text.strip().rstrip(".")
            source_name = source or "the available evidence"

            parts.append(
                f"The recommendation from {source_name} is: "
                f"{clean_recommendation}."
            )

        if evidence_level:
            parts.append(
                f"The reported evidence classification is "
                f"{evidence_level}."
            )

        if recommendation.get("conflict"):
            parts.append(
                "A potential evidence conflict was identified; "
                "specialist review is required."
            )

        warnings = recommendation.get("warnings") or []

        if warnings:
            parts.append(
                "Evidence review is needed because: "
                + " ".join(
                    str(warning).strip().rstrip(".") + "."
                    for warning in warnings
                    if str(warning).strip()
                )
            )
        elif recommendation.get("requires_review"):
            parts.append(
                "Additional evidence review is recommended "
                "before finalizing the result."
            )

        parts.append(
            "This result supports clinical decision-making "
            "and is not a substitute for review by a qualified "
            "healthcare professional."
        )

        if len(parts) == 1:
            return (
                "Insufficient structured information is available "
                "to explain this result. Clinical review is needed."
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
