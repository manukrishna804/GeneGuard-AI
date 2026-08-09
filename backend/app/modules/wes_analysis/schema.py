# Pydantic v2 schemas for the WES Analysis module (Module 1).

"""
Schemas:
    VariantInput        - request body for /test-variant
    DatasourceResult    - per-datasource status + raw data envelope
    ExtractionInfo      - source and confidence of variant extraction
    EnsemblInfo         - summarized Ensembl response
    ClinVarInfo         - summarized ClinVar response
    OMIMInfo            - summarized OMIM response
    GnomADInfo          - summarized gnomAD response
    HPOInfo             - HPO phenotype mapping
    VariantResult       - a single extracted variant + its summarized evidence
    WESAnalysisResponse - top-level response for /analyze and /test-variant
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class VariantInput(BaseModel):
    """
    Manually supplied variant for the /test-variant endpoint.
    All fields except 'gene' are optional because real WES reports
    may omit any of them.
    """
    gene: str
    transcript: Optional[str] = None
    cdna: Optional[str] = None          # e.g. "c.722G>A"
    protein: Optional[str] = None       # e.g. "p.Arg241His"
    rsid: Optional[str] = None          # e.g. "rs5030859"
    zygosity: Optional[str] = None      # "HET", "HOM", "HEMIZYGOUS", etc.
    classification: Optional[str] = None
    variant_type: Optional[str] = None

# ---------------------------------------------------------------------------
# Internal helper schema (unchanged)
# ---------------------------------------------------------------------------

class DatasourceResult(BaseModel):
    """
    Wraps the result from a single external data source.

    status values:
        "success"       - data returned successfully
        "not_found"     - query succeeded but no record exists
        "error"         - HTTP or connection failure
        "skipped"       - not enough information to query (e.g. no gene name)
    """
    status: str
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

# ---------------------------------------------------------------------------
# New summary models for response
# ---------------------------------------------------------------------------

class ExtractionInfo(BaseModel):
    source: str            # "variant_table" or "fallback_text"
    confidence: str        # "high" or "low"

class PubMedArticle(BaseModel):
    pmid: str
    title: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[str] = None
    authors: Optional[str] = None

class OMIMPhenotype(BaseModel):
    mim_number: Optional[str] = None
    title: Optional[str] = None
    inheritance: Optional[str] = None

class EnsemblInfo(BaseModel):
    status: str
    matched: bool
    variant_id: Optional[str] = None
    genomic_change: Optional[str] = None
    hgvs_g: Optional[str] = None
    consequence: Optional[str] = None
    chromosome: Optional[str] = None
    position: Optional[int] = None
    ref_allele: Optional[str] = None
    alt_allele: Optional[str] = None
    hgvsc: Optional[str] = None
    hgvsp: Optional[str] = None
    gene_id: Optional[str] = None
    transcript_id: Optional[str] = None
    biotype: Optional[str] = None
    strand: Optional[int] = None
    impact: Optional[str] = None
    amino_acids: Optional[str] = None
    codons: Optional[str] = None
    additional_ids: List[str] = []

class ClinVarInfo(BaseModel):
    status: str
    matched: bool
    variation_id: Optional[str] = None
    accession: Optional[str] = None
    clinical_significance: Optional[str] = None
    review_status: Optional[str] = None
    condition: Optional[str] = None
    submission_count: Optional[int] = None
    last_evaluated: Optional[str] = None
    conflict_status: Optional[str] = None
    associated_conditions: List[str] = []
    classifications_summary: Optional[Dict[str, Any]] = None
    supporting_pmids: List[str] = []

class OMIMInfo(BaseModel):
    status: str
    matched: bool
    mim_number: Optional[str] = None
    title: Optional[str] = None
    inheritance: Optional[str] = None
    gene_mim_number: Optional[str] = None
    phenotypes: List[OMIMPhenotype] = []

class GnomADInfo(BaseModel):
    status: str
    matched: bool
    allele_frequency: Optional[float] = None
    pop_max_frequency: Optional[float] = None
    allele_count: Optional[int] = None
    allele_number: Optional[int] = None
    homozygote_count: Optional[int] = None
    population_frequencies: Optional[Dict[str, float]] = None

class HPOInfo(BaseModel):
    hpo_id: str
    phenotype: str

# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class VariantResult(BaseModel):
    """
    A single variant with its extracted fields and external evidence.
    """
    # Extracted variant fields (all optional — WES reports vary in completeness)
    gene: Optional[str] = None
    transcript: Optional[str] = None
    cdna: Optional[str] = None
    protein: Optional[str] = None
    rsid: Optional[str] = None
    zygosity: Optional[str] = None
    classification: Optional[str] = None
    variant_type: Optional[str] = None

    # Validation
    is_valid: bool = True
    validation_message: Optional[str] = None

    # Normalized HGVS (simple concatenation)
    normalized_hgvs: Optional[str] = None

    # External evidence (summarized)
    ensembl: EnsemblInfo
    clinvar: ClinVarInfo
    gnomad: Optional[GnomADInfo] = None
    omim: Optional[OMIMInfo] = None
    hpo: List[HPOInfo] = []
    pubmed: List[str] = []
    pubmed_details: List[PubMedArticle] = []

class WESAnalysisResponse(BaseModel):
    """
    Top-level response for both /analyze and /test-variant endpoints.
    """
    status: str                         # "success" | "partial" | "error"
    extraction: ExtractionInfo
    variants: List[VariantResult] = []
    message: Optional[str] = None      # set when status != "success"


