from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# ENUMS
# ============================================================

class ParentSex(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class Zygosity(str, Enum):
    HOMOZYGOUS = "homozygous"
    HETEROZYGOUS = "heterozygous"
    HEMIZYGOUS = "hemizygous"
    UNKNOWN = "unknown"


class VariantClassification(str, Enum):
    PATHOGENIC = "pathogenic"
    LIKELY_PATHOGENIC = "likely_pathogenic"
    VUS = "vus"
    LIKELY_BENIGN = "likely_benign"
    BENIGN = "benign"
    UNKNOWN = "unknown"


class ConsanguinityType(str, Enum):
    UNRELATED = "unrelated"
    FIRST_COUSIN = "first_cousin"
    SECOND_COUSIN = "second_cousin"
    OTHER = "other"
    UNKNOWN = "unknown"


class HealthStatus(str, Enum):
    AFFECTED = "affected"
    UNAFFECTED = "unaffected"
    UNKNOWN = "unknown"


# ============================================================
# VARIANT DATA
# ============================================================

class GeneticVariant(BaseModel):
    """
    Structured representation of a variant belonging to one parent.
    """

    gene: str = Field(..., description="Gene symbol, e.g. HBB")

    chromosome: Optional[str] = None
    position: Optional[int] = None

    reference: Optional[str] = None
    alternate: Optional[str] = None

    variant_name: Optional[str] = Field(
        default=None,
        description="HGVS or other normalized variant representation"
    )

    zygosity: Zygosity = Zygosity.UNKNOWN

    classification: VariantClassification = (
        VariantClassification.UNKNOWN
    )

    condition: Optional[str] = Field(
        default=None,
        description="Associated genetic condition"
    )

    inheritance: Optional[str] = Field(
        default=None,
        description="Known inheritance pattern of the associated condition"
    )

    evidence_sources: List[str] = Field(
        default_factory=list,
        description="Sources such as ClinVar, OMIM, Orphanet"
    )


# ============================================================
# PARENT GENETIC PROFILE
# ============================================================

class ParentGeneticProfile(BaseModel):
    """
    Genetic information for one prospective parent.
    """

    parent_id: str

    sex: ParentSex = ParentSex.UNKNOWN

    variants: List[GeneticVariant] = Field(
        default_factory=list
    )


# ============================================================
# FAMILY HISTORY
# ============================================================

class FamilyHistoryEntry(BaseModel):
    """
    Structured information about one family member.
    """

    relationship: str = Field(
        ...,
        description="Relationship to the parent, e.g. sibling, uncle, grandparent"
    )

    sex: ParentSex = ParentSex.UNKNOWN

    health_status: HealthStatus = HealthStatus.UNKNOWN

    condition: Optional[str] = None

    known_variant: Optional[str] = None

    inheritance_pattern: Optional[str] = None

    notes: Optional[str] = None


# ============================================================
# CONSANGUINITY INFORMATION
# ============================================================

class ConsanguinityInfo(BaseModel):
    """
    Biological relationship information between the two parents.
    """

    relationship: ConsanguinityType = ConsanguinityType.UNKNOWN

    description: Optional[str] = Field(
        default=None,
        description="Additional description if relationship is 'other'"
    )


# ============================================================
# PREVIOUS PREGNANCY / CHILD INFORMATION
# ============================================================

class PreviousChildHistory(BaseModel):
    """
    Information about a previous child relevant to inherited-condition
    assessment.
    """

    condition: Optional[str] = None

    affected: bool = False

    genetically_confirmed: Optional[bool] = None

    known_variant: Optional[str] = None

    notes: Optional[str] = None


# ============================================================
# COMPLETE MODULE 4 REQUEST
# ============================================================

class OffspringRiskAssessmentRequest(BaseModel):
    """
    Main structured input for Module 4.
    """

    parent1: ParentGeneticProfile

    parent2: ParentGeneticProfile

    family_history: List[FamilyHistoryEntry] = Field(
        default_factory=list
    )

    consanguinity: ConsanguinityInfo = Field(
        default_factory=ConsanguinityInfo
    )

    previous_children: List[PreviousChildHistory] = Field(
        default_factory=list
    )

    known_or_suspected_condition: Optional[str] = None


# ============================================================
# RISK RESULT
# ============================================================

class OffspringRiskResult(BaseModel):
    """
    Result for one disease/condition.
    """

    gene: Optional[str] = None

    condition: str

    inheritance: str

    parent1_status: str

    parent2_status: str

    affected_probability: float

    carrier_probability: float

    unaffected_probability: float

    evidence_sources: List[str] = Field(
        default_factory=list
    )

    explanation: str


# ============================================================
# COMPLETE MODULE 4 RESPONSE
# ============================================================

class OffspringRiskAssessmentResponse(BaseModel):
    """
    Complete response returned by Module 4.
    """

    assessment_id: Optional[str] = None

    status: str

    risks: List[OffspringRiskResult] = Field(
        default_factory=list
    )

    shared_risk_count: int = 0

    uncertain_variant_count: int = 0

    consanguinity_context: Optional[str] = None

    limitations: List[str] = Field(
        default_factory=list
    )