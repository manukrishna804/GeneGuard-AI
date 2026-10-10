from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# INPUT SCHEMAS
# ============================================================

class MedicationInput(BaseModel):
    name: str
    dosage: Optional[str] = None


class VariantInput(BaseModel):
    chromosome: Optional[str] = None
    position: Optional[int] = None
    gene: Optional[str] = None
    reference: Optional[str] = None
    alternate: Optional[str] = None
    genotype: Optional[str] = None
    rsid: Optional[str] = None
    star_allele: Optional[str] = None



class PharmacogenomicsRequest(BaseModel):
    """
    Input provided directly to Module 5 by the user/frontend.
    """

    patient_id: str

    clinical_indication: Optional[str] = None

    medications: List[MedicationInput] = Field(default_factory=list)

    variants: List[VariantInput] = Field(default_factory=list)


# ============================================================
# DIPLOTYPE / PHENOTYPE
# ============================================================

class DiplotypeResult(BaseModel):
    gene: str
    diplotype: Optional[str] = None
    star_alleles: List[str] = Field(default_factory=list)


class PhenotypeResult(BaseModel):
    gene: str
    diplotype: Optional[str] = None
    phenotype: Optional[str] = None
    activity_score: Optional[float] = None


# ============================================================
# EVIDENCE
# ============================================================

class CPICEvidence(BaseModel):
    guideline_id: Optional[str] = None
    evidence_level: Optional[str] = None
    recommendation: Optional[str] = None
    source: Optional[str] = None


class PharmGKBEvidence(BaseModel):
    evidence_level: Optional[str] = None
    annotation: Optional[str] = None
    source: Optional[str] = None


class PharmVarEvidence(BaseModel):
    allele: Optional[str] = None
    definition: Optional[str] = None
    source: Optional[str] = None


class DrugBankEvidence(BaseModel):
    drug: Optional[str] = None
    interaction: Optional[str] = None
    pharmacokinetic_context: Optional[str] = None
    source: Optional[str] = None


class EvidenceBundle(BaseModel):
    cpic: Optional[CPICEvidence] = None
    pharmgkb: Optional[PharmGKBEvidence] = None
    pharmvar: Optional[List[PharmVarEvidence]] = None
    drugbank: Optional[DrugBankEvidence] = None


# ============================================================
# RECOMMENDATION
# ============================================================

class PharmacogenomicRecommendation(BaseModel):
    drug: str
    gene: str

    diplotype: Optional[str] = None
    phenotype: Optional[str] = None
    activity_score: Optional[float] = None

    recommendation: Optional[str] = None

    evidence_level: Optional[str] = None
    source: Optional[str] = None

    evidence: Optional[EvidenceBundle] = None

    conflict: bool = False
    conflict_message: Optional[str] = None

    explanation: Optional[str] = None


# ============================================================
# FINAL RESPONSE
# ============================================================

class PharmacogenomicsResponse(BaseModel):
    """
    Final structured response returned by Module 5 to React.
    """

    patient_id: str

    # Demo-facing audit fields: a variant annotation is not a validated
    # diplotype or a clinical recommendation.
    analysis_status: str = "review_required"
    review_message: Optional[str] = None
    detected_variants: List[Dict[str, Any]] = Field(default_factory=list)
    diplotypes: List[Dict[str, Any]] = Field(default_factory=list)
    phenotypes: List[Dict[str, Any]] = Field(default_factory=list)

    recommendations: List[PharmacogenomicRecommendation] = Field(
        default_factory=list
    )

    flagged_conflicts: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    confidence: Optional[float] = None

    specialist: Optional[str] = None
