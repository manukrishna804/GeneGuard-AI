# Pydantic v2 schemas for WES Variant Annotation & Retrieval

"""
Schemas:
    VariantInput            - Request payload for /test-variant
    DatasourceResult        - Wrap envelope for external API lookups
    ReportedVariant         - Variant details extracted directly from WES report
    NormalizedVariant       - Standardized genomic HGVS / rsID notations
    GeneInfo                - Symbol, ID, chromosome, description, aliases
    EnsemblAnnotation       - Annotations from Ensembl REST API / VEP
    ClinVarAnnotation       - Annotations from NCBI ClinVar E-utilities
    GnomADAnnotation        - Allele frequencies and population counts from gnomAD
    OMIMAnnotation          - MIM numbers, disease titles, phenotypes, inheritance
    LiteratureAnnotation    - PubMed ID counts and article references
    DatabaseAnnotations     - Combined database annotations object
    VerificationInfo        - Identity verification & database match statuses
    SingleVariantAnnotation - Complete single variant annotation bundle
    WESAnalysisResponse     - Top-level response for /analyze and /test-variant
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Input & Helper Schemas
# ---------------------------------------------------------------------------

class VariantInput(BaseModel):
    """
    Manually supplied variant for the /test-variant endpoint.
    """
    gene: str
    transcript: Optional[str] = None
    cdna: Optional[str] = None          # e.g. "c.722G>A"
    protein: Optional[str] = None       # e.g. "p.Arg241His"
    rsid: Optional[str] = None          # e.g. "rs5030859"
    zygosity: Optional[str] = None      # "HET", "HOM", "HEMIZYGOUS", etc.
    classification: Optional[str] = None
    variant_type: Optional[str] = None


class DatasourceResult(BaseModel):
    """
    Wraps the raw response or error from an external genomic API.
    """
    status: str
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


# ---------------------------------------------------------------------------
# Core Variant & Public Database Annotation Models
# ---------------------------------------------------------------------------

class ReportedVariant(BaseModel):
    """
    Variant details extracted from the original report (unaltered).
    """
    gene: Optional[str] = None
    transcript: Optional[str] = None
    cdna: Optional[str] = None
    protein: Optional[str] = None
    zygosity: Optional[str] = None
    classification: Optional[str] = None
    variant_type: Optional[str] = None


class NormalizedVariant(BaseModel):
    """
    Resolved genomic identity and standard HGVS notations.
    """
    hgvs_c: Optional[str] = None
    hgvs_p: Optional[str] = None
    hgvs_g: Optional[str] = None
    rsid: Optional[str] = None
    spdi: Optional[str] = None


class GeneInfo(BaseModel):
    """
    Comprehensive gene-level information retrieved from public databases.
    """
    symbol: Optional[str] = None
    gene_id: Optional[str] = None
    chromosome: Optional[str] = None
    cytoband: Optional[str] = None
    strand: Optional[str] = None
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)


class EnsemblAnnotation(BaseModel):
    """
    Ensembl REST / VEP variant annotations.
    """
    matched: bool = False
    consequence: Optional[str] = None
    hgvs_g: Optional[str] = None
    spdi: Optional[str] = None
    rsid: Optional[str] = None
    biotype: Optional[str] = None
    gene_id: Optional[str] = None
    transcript_id: Optional[str] = None
    impact: Optional[str] = None
    in_silico_predictions: Dict[str, str] = Field(default_factory=dict)


class ClinVarAnnotation(BaseModel):
    """
    NCBI ClinVar accession and evidence annotations.
    """
    matched: bool = False
    variation_id: Optional[str] = None
    accession: Optional[str] = None
    clinical_significance: Optional[str] = None
    review_status: Optional[str] = None
    last_evaluated: Optional[str] = None
    variation_type: Optional[str] = None
    conditions: List[str] = Field(default_factory=list)
    submission_count: Optional[Any] = None
    conflict: bool = False
    supporting_pmids: List[str] = Field(default_factory=list)


class GnomADAnnotation(BaseModel):
    """
    gnomAD population frequencies and allele counts.
    """
    matched: bool = False
    allele_frequency: Optional[float] = None
    allele_count: Optional[int] = None
    allele_number: Optional[int] = None
    homozygote_count: Optional[int] = None
    populations: Dict[str, Any] = Field(default_factory=dict)


class OMIMAnnotation(BaseModel):
    """
    Online Mendelian Inheritance in Man (OMIM) disease & phenotype annotations.
    """
    matched: bool = False
    mim_number: Optional[str] = None
    title: Optional[str] = None
    inheritance: Optional[str] = None
    phenotypes: List[Dict[str, Any]] = Field(default_factory=list)


class HPOAnnotation(BaseModel):
    """
    Human Phenotype Ontology (HPO) clinical term annotations.
    """
    matched: bool = False
    hpo_terms: List[Dict[str, str]] = Field(default_factory=list)


class LiteratureAnnotation(BaseModel):
    """
    PubMed literature evidence counts, article IDs, and metadata.
    """
    pubmed_count: int = 0
    pubmed_ids: List[str] = Field(default_factory=list)
    articles: List[Dict[str, Any]] = Field(default_factory=list)


class DatabaseAnnotations(BaseModel):
    """
    Combined public database evidence for a variant.
    """
    ensembl: Optional[EnsemblAnnotation] = None
    clinvar: Optional[ClinVarAnnotation] = None
    gnomad: Optional[GnomADAnnotation] = None
    omim: Optional[OMIMAnnotation] = None
    hpo: Optional[HPOAnnotation] = None
    literature: Optional[LiteratureAnnotation] = None


class VerificationInfo(BaseModel):
    """
    Cross-database identity verification, match flags, and classification discrepancies.
    """
    variant_identity_verified: bool = False
    ensembl_match: bool = False
    clinvar_match: bool = False
    gnomad_match: bool = False
    discrepancies: List[Dict[str, str]] = Field(default_factory=list)


class SingleVariantAnnotation(BaseModel):
    """
    Clean bundle for a single variant and all its public database annotations.
    """
    reported_variant: ReportedVariant
    normalized_variant: NormalizedVariant
    gene: GeneInfo
    annotations: DatabaseAnnotations
    verification: VerificationInfo


# ---------------------------------------------------------------------------
# Top-Level API Response Schema
# ---------------------------------------------------------------------------

class WESAnalysisResponse(BaseModel):
    """
    Top-level API response for /analyze and /test-variant endpoints.
    Supports both single-variant top-level fields and multi-variant list.
    """
    status: str = "success"

    # Single variant top-level format
    reported_variant: Optional[ReportedVariant] = None
    normalized_variant: Optional[NormalizedVariant] = None
    gene: Optional[GeneInfo] = None
    annotations: Optional[DatabaseAnnotations] = None
    verification: Optional[VerificationInfo] = None

    # Multi-variant list format
    variants: Optional[List[SingleVariantAnnotation]] = None

    message: Optional[str] = None
