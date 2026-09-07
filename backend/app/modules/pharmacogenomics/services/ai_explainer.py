import json
import os
from typing import Any, Dict, Optional

from app.modules.pharmacogenomics.config import pgx_settings


def generate_fallback_explanations(evidence: Dict[str, Any]) -> Dict[str, str]:
    """
    Deterministic rule-based explanation generator (Zero Hallucination Fallback).
    """
    drug = evidence["gene_drug_pair"]["drug"]
    gene = evidence["genomic_profile"]["gene"]
    diplotype = evidence["genomic_profile"]["diplotype"]
    phenotype = evidence["genomic_profile"]["phenotype"]
    rec = evidence["guideline_evidence"]["cpic_recommendation"]
    implication = evidence["guideline_evidence"]["clinical_implication"]
    actionability = evidence["guideline_evidence"]["actionability"]

    if "Contraindicated" in actionability or "Alternative" in actionability:
        patient_text = (
            f"Your genetic test shows you have the {diplotype} variation in the {gene} gene, "
            f"meaning your body is categorized as a '{phenotype}'. This affects how you process {drug}. "
            f"Because of this, {drug} may not work properly or could cause increased side effects. "
            f"Your doctor is advised to consider a safe, alternative medication."
        )
    elif "Dose Adjustment" in actionability:
        patient_text = (
            f"Your test shows the {diplotype} result for {gene} ({phenotype}). "
            f"Your body processes {drug} differently than average. Your healthcare team may adjust "
            f"your starting dosage to ensure the medicine is both effective and safe for you."
        )
    else:
        patient_text = (
            f"Your {gene} genetic test result ({diplotype}, {phenotype}) is within normal parameters for {drug}. "
            f"Standard dosage is expected to work as intended."
        )

    clinician_text = (
        f"Patient genotype is {gene} {diplotype} ({phenotype}). "
        f"Clinical Implication: {implication} "
        f"Guideline Guidance: {rec}"
    )

    return {
        "patient_explanation": patient_text,
        "clinician_summary": clinician_text
    }


async def generate_ai_explanations(evidence: Dict[str, Any]) -> Dict[str, str]:
    """
    Stage 10: Generate plain-language patient explanation and clinician summary via LLM or deterministic fallback.
    """
    # Check if Groq or OpenAI is configured
    groq_key = os.getenv("GROQ_API_KEY") or pgx_settings.GROQ_API_KEY
    openai_key = os.getenv("OPENAI_API_KEY") or pgx_settings.OPENAI_API_KEY

    # If neither key is present, return deterministic template
    if not groq_key and not openai_key:
        return generate_fallback_explanations(evidence)

    # If keys exist, attempt structured LLM generation
    prompt = (
        "You are an expert Clinical Pharmacogenomics AI assistant in GeneGuard. "
        "Given the following structured PGx evidence JSON, produce two short explanations:\n"
        "1. 'patient_explanation': A clear, compassionate, 6th-to-8th-grade reading level explanation for the patient.\n"
        "2. 'clinician_summary': A precise 2-sentence clinical pharmacology summary citing the guideline.\n\n"
        "IMPORTANT RULES:\n"
        "- Do NOT alter or override the recommendation in the JSON.\n"
        "- Do NOT invent new gene names or side effects.\n"
        "- Return strictly a valid JSON object with keys 'patient_explanation' and 'clinician_summary'.\n\n"
        f"EVIDENCE JSON:\n{json.dumps(evidence, indent=2)}"
    )

    try:
        if groq_key:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=groq_key)
            response = await client.chat.completions.create(
                model=pgx_settings.DEFAULT_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            if "patient_explanation" in parsed and "clinician_summary" in parsed:
                return parsed
        elif openai_key:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=openai_key)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            if "patient_explanation" in parsed and "clinician_summary" in parsed:
                return parsed
    except Exception:
        # Fallback seamlessly on any LLM or network error
        pass

    return generate_fallback_explanations(evidence)
