"""
services/medication_lookup.py
==============================
Pharmacogenomics lookup service for GeneGuard-AI.

Provides a stub CPIC-style recommendation engine based on well-known
gene/genotype → phenotype mappings. When PharmGKB/CPIC API credentials
are available, replace _cpic_api_lookup() with a real HTTP call and set
USE_API = True.

Reference data sourced from CPIC guidelines (https://cpicpgx.org/guidelines/).
"""

from __future__ import annotations

from typing import Dict, Optional


# ---------------------------------------------------------------------------
# Configuration flag — flip to True when live API credentials are available
# ---------------------------------------------------------------------------
USE_API: bool = False


# ---------------------------------------------------------------------------
# Built-in stub knowledge base
# Gene → { genotype → { metabolizer_status, recommendation, confidence } }
# ---------------------------------------------------------------------------

_CPIC_STUB: Dict[str, Dict[str, Dict[str, str]]] = {
    "CYP2D6": {
        "*1/*1": {
            "metabolizer_status": "normal",
            "recommendation": (
                "Normal metabolizer. Use standard dosing as recommended in the prescribing information."
            ),
            "confidence": "strong",
        },
        "*1/*4": {
            "metabolizer_status": "intermediate",
            "recommendation": (
                "Intermediate metabolizer. Consider a 25% dose reduction for drugs with "
                "CYP2D6-dependent activation (e.g. codeine, tamoxifen). Monitor for reduced efficacy."
            ),
            "confidence": "strong",
        },
        "*4/*4": {
            "metabolizer_status": "poor",
            "recommendation": (
                "Poor metabolizer. Avoid prodrugs requiring CYP2D6 activation (e.g. codeine, "
                "tramadol). For tricyclic antidepressants, use 50% of normal starting dose and "
                "titrate based on response."
            ),
            "confidence": "strong",
        },
        "*1/*2": {
            "metabolizer_status": "normal",
            "recommendation": (
                "Normal metabolizer. Standard dosing recommended."
            ),
            "confidence": "moderate",
        },
        "*2/*2": {
            "metabolizer_status": "ultrarapid",
            "recommendation": (
                "Ultrarapid metabolizer. Risk of opioid toxicity with codeine — avoid use. "
                "For antidepressants, standard doses may be subtherapeutic; consider alternatives."
            ),
            "confidence": "strong",
        },
    },
    "CYP2C19": {
        "*1/*1": {
            "metabolizer_status": "normal",
            "recommendation": (
                "Normal metabolizer. Use standard clopidogrel or PPI dosing."
            ),
            "confidence": "strong",
        },
        "*1/*2": {
            "metabolizer_status": "intermediate",
            "recommendation": (
                "Intermediate metabolizer for clopidogrel — consider alternative antiplatelet therapy "
                "(e.g. prasugrel, ticagrelor) in high-risk ACS patients."
            ),
            "confidence": "strong",
        },
        "*2/*2": {
            "metabolizer_status": "poor",
            "recommendation": (
                "Poor metabolizer. Clopidogrel is predicted to have markedly reduced antiplatelet "
                "effect. Use alternative agents. PPIs may have increased efficacy — consider dose reduction."
            ),
            "confidence": "strong",
        },
        "*17/*17": {
            "metabolizer_status": "ultrarapid",
            "recommendation": (
                "Ultrarapid metabolizer. PPIs may have reduced efficacy at standard doses. "
                "Clopidogrel bioactivation may be enhanced."
            ),
            "confidence": "moderate",
        },
    },
    "TPMT": {
        "*1/*1": {
            "metabolizer_status": "normal",
            "recommendation": (
                "Normal TPMT activity. Use standard thiopurine dosing (azathioprine, mercaptopurine)."
            ),
            "confidence": "strong",
        },
        "*1/*3A": {
            "metabolizer_status": "intermediate",
            "recommendation": (
                "Intermediate TPMT activity. Reduce starting thiopurine dose by 30–70%. "
                "Monitor CBC for myelosuppression."
            ),
            "confidence": "strong",
        },
        "*3A/*3A": {
            "metabolizer_status": "poor",
            "recommendation": (
                "Poor TPMT metabolizer. Very high risk of life-threatening myelosuppression. "
                "Use 10% of standard dose or switch to alternative immunosuppressant."
            ),
            "confidence": "strong",
        },
    },
    "DPYD": {
        "*1/*1": {
            "metabolizer_status": "normal",
            "recommendation": (
                "Normal DPD activity. Standard 5-fluorouracil/capecitabine dosing."
            ),
            "confidence": "strong",
        },
        "*2A/*1": {
            "metabolizer_status": "intermediate",
            "recommendation": (
                "Intermediate DPD activity. Reduce 5-FU/capecitabine starting dose by 50%. "
                "Increase dose in subsequent cycles only with close monitoring for toxicity."
            ),
            "confidence": "strong",
        },
        "*2A/*2A": {
            "metabolizer_status": "poor",
            "recommendation": (
                "Complete DPD deficiency. 5-fluorouracil and capecitabine are contraindicated "
                "due to risk of fatal toxicity."
            ),
            "confidence": "strong",
        },
    },
    "SLCO1B1": {
        "*1a/*1a": {
            "metabolizer_status": "normal",
            "recommendation": (
                "Normal SLCO1B1 function. Routine statin dosing."
            ),
            "confidence": "strong",
        },
        "*5/*1a": {
            "metabolizer_status": "intermediate",
            "recommendation": (
                "Decreased SLCO1B1 function. Increased simvastatin plasma exposure. "
                "Limit simvastatin dose to ≤20 mg/day; consider alternative statins (e.g. pravastatin, rosuvastatin)."
            ),
            "confidence": "strong",
        },
        "*5/*5": {
            "metabolizer_status": "poor",
            "recommendation": (
                "Markedly decreased SLCO1B1 function. High risk of simvastatin-associated myopathy. "
                "Avoid simvastatin. Use pravastatin or rosuvastatin."
            ),
            "confidence": "strong",
        },
    },
}


# ---------------------------------------------------------------------------
# Internal lookup helpers
# ---------------------------------------------------------------------------

def _stub_lookup(gene: str, genotype: str) -> Optional[Dict[str, str]]:
    """Exact match first, then try reversed allele order."""
    gene_upper = gene.upper().strip()
    geno_clean = genotype.strip()

    gene_data = _CPIC_STUB.get(gene_upper)
    if not gene_data:
        return None

    result = gene_data.get(geno_clean)
    if result:
        return result

    # Try reversed allele order (e.g. "*4/*1" → "*1/*4")
    if "/" in geno_clean:
        parts = geno_clean.split("/", 1)
        reversed_geno = f"{parts[1]}/{parts[0]}"
        result = gene_data.get(reversed_geno)
        if result:
            return result

    return None


def _cpic_api_lookup(gene: str, genotype: str) -> Optional[Dict[str, str]]:
    """
    Placeholder for live CPIC/PharmGKB API integration.

    When implementing:
      1. Set USE_API = True
      2. Add CPIC_API_KEY to .env and settings
      3. Make an HTTP GET to https://api.cpicpgx.org/v1/recommendation
         with gene and diplotype params
      4. Parse and return the recommendation dict
    """
    raise NotImplementedError(
        "Live CPIC API integration not yet implemented. Set USE_API = False to use stub data."
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def lookup_recommendation(gene: str, genotype: str) -> Dict[str, Optional[str]]:
    """
    Returns a pharmacogenomics recommendation for the given gene + genotype.

    Args:
        gene:      Gene symbol, e.g. "CYP2D6", "TPMT"
        genotype:  Diplotype notation, e.g. "*1/*4", "*2A/*2A"

    Returns:
        dict with keys:
            gene, genotype, metabolizer_status, cpic_recommendation,
            confidence_level, source
    """
    if USE_API:
        result = _cpic_api_lookup(gene, genotype)
    else:
        result = _stub_lookup(gene, genotype)

    if result:
        return {
            "gene": gene.upper(),
            "genotype": genotype,
            "metabolizer_status": result.get("metabolizer_status"),
            "cpic_recommendation": result.get("recommendation"),
            "confidence_level": result.get("confidence"),
            "source": "cpic_api" if USE_API else "stub",
        }

    return {
        "gene": gene.upper(),
        "genotype": genotype,
        "metabolizer_status": None,
        "cpic_recommendation": (
            f"No CPIC recommendation found for {gene.upper()} genotype '{genotype}'. "
            "Consult pharmacogenomics specialist or check cpicpgx.org."
        ),
        "confidence_level": None,
        "source": "stub",
    }
