from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VariantInput(BaseModel):
    gene: str = Field(..., description="Gene symbol, e.g., CYP2C19")
    hgvs_c: Optional[str] = Field(None, description="Coding DNA HGVS notation, e.g., c.681G>A")
    hgvs_p: Optional[str] = Field(None, description="Protein HGVS notation, e.g., p.Pro227=")
    rsid: Optional[str] = Field(None, description="dbSNP rsID, e.g., rs4244285")
    zygosity: Optional[str] = Field("heterozygous", description="Zygosity: heterozygous, homozygous_alt, homozygous_ref")
    star_allele: Optional[str] = Field(None, description="Explicit star-allele if known, e.g., *2")


class PGxAnalyzeRequest(BaseModel):
    patient_id: int = Field(..., description="ID of the patient")
    medications: List[str] = Field(..., description="List of medications to evaluate")
    variants: Optional[List[VariantInput]] = Field(default=None, description="Optional custom list of variants. If omitted and use_latest_wes is true, extracts from patient's latest WES report.")
    use_latest_wes: bool = Field(default=True, description="Whether to automatically load variants from the patient's WES report")


class DiplotypeCall(BaseModel):
    gene: str
    diplotype: str
    activity_score: Optional[float] = None
    phenotype: str
    phenotype_code: Optional[str] = None
    evidence_alleles: List[str] = []
    source: str = "PharmVar / CPIC Activity Score"


class GeneDrugRecommendation(BaseModel):
    drug: str
    gene: str
    diplotype: str
    phenotype: str
    activity_score: Optional[float] = None
    actionability: str
    recommendation: str
    clinical_implication: str
    evidence_level: str
    pharmgkb_level: Optional[str] = None
    source: str
    fda_label_status: Optional[str] = None
    conflict: bool = False
    conflict_details: Optional[str] = None
    requires_specialist_review: bool = False
    specialist: str = "Clinical Pharmacist"
    rank_priority: int = 1
    patient_explanation: str
    clinician_summary: str


class PGxPipelineResponse(BaseModel):
    report_id: Optional[int] = None
    patient_id: int
    timestamp: datetime
    status: str
    total_drugs_evaluated: int
    matched_gene_drug_pairs: int
    overall_confidence: float
    flagged_conflicts: List[Dict[str, Any]] = []
    diplotype_calls: List[DiplotypeCall] = []
    recommendations: List[GeneDrugRecommendation] = []
    unmatched_drugs: List[str] = []


class GeneDrugPairInfo(BaseModel):
    drug_name: str
    brand_names: List[str] = []
    primary_gene: str
    secondary_genes: List[str] = []
    therapeutic_area: str
    cpic_level: str
    pharmgkb_level: str
    fda_label_status: str


class PGxReportSummary(BaseModel):
    id: int
    patient_id: int
    status: str
    confidence_score: float
    flagged_conflicts_count: int
    medications_evaluated: Optional[List[str]] = None
    created_at: datetime
