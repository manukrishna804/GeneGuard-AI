from typing import Any, Dict, List, Optional

from .pharmacogene_filter import filter_pharmacogenes
from .diplotype_caller import call_diplotypes
from .phenotype_mapper import map_phenotypes
from .drug_matcher import match_drugs_to_genes

from .cpic_service import fetch_cpic_guideline
from .pharmgkb_service import fetch_pharmgkb_evidence
from .pharmvar_service import PharmVarService
from .drugbank_service import fetch_drugbank_context

from .evidence_aggregator import aggregate_multiple_evidence
from .conflict_detector import detect_multiple_conflicts
from .recommendation_engine import build_recommendations
from .confidence import calculate_confidence
from .ai_explainer import explain_recommendation


async def run_pharmacogenomics_pipeline(
    variants: List[Dict[str, Any]],
    medications: List[Dict[str, Any]],
    clinical_indication: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main orchestration pipeline for Pharmacogenomics Module 5.

    Pipeline:

    Variants
        ↓
    Pharmacogene Filtering
        ↓
    Diplotype Calling
        ↓
    Phenotype Mapping
        ↓
    Drug-Gene Matching
        ↓
    Evidence Retrieval
        ↓
    Evidence Aggregation
        ↓
    Conflict Detection
        ↓
    Rule-Based Recommendation
        ↓
    Confidence Calculation
        ↓
    AI Explanation
        ↓
    Final Structured Result
    """

    # ---------------------------------------------------------
    # 1. Filter pharmacogenes
    # ---------------------------------------------------------

    pharmacogene_variants = filter_pharmacogenes(variants)

    # ---------------------------------------------------------
    # 2. Call diplotypes / star alleles
    # ---------------------------------------------------------

    diplotype_results = call_diplotypes(pharmacogene_variants)

    # ---------------------------------------------------------
    # 3. Map diplotypes to phenotypes
    # ---------------------------------------------------------

    phenotype_results = map_phenotypes(diplotype_results)

    # ---------------------------------------------------------
    # 4. Match medications with pharmacogenes
    # ---------------------------------------------------------

    # Only map a drug when the diplotype supports a phenotype. A detected
    # variant alone must not trigger a genotype-specific recommendation.
    actionable_phenotypes = [
        result for result in phenotype_results
        if result.get("phenotype") is not None
    ]

    matched_pairs = match_drugs_to_genes(
        medications=medications,
        phenotype_results=actionable_phenotypes,
    )

    # ---------------------------------------------------------
    # 5. Prepare evidence containers
    # ---------------------------------------------------------

    cpic_results: Dict[str, Dict[str, Any]] = {}
    pharmgkb_results: Dict[str, Dict[str, Any]] = {}
    pharmvar_results: Dict[str, List[Dict[str, Any]]] = {}
    drugbank_results: Dict[str, Dict[str, Any]] = {}

    pharmvar_service = PharmVarService()

    # ---------------------------------------------------------
    # 6. Retrieve evidence for each gene-drug pair
    # ---------------------------------------------------------

    for pair in matched_pairs:
        gene = pair.get("gene")
        drug = pair.get("drug")
        guideline_id = pair.get("cpic_guideline_id")

        if not gene or not drug:
            continue

        key = f"{gene}:{drug}"

       
        # CPIC
        cpic_results[key] = await fetch_cpic_guideline(
            gene=gene,
            drug=drug,
            phenotype=pair.get("phenotype"),
            population=clinical_indication,
            guideline_id=guideline_id,
        )


        # PharmGKB
        pharmgkb_results[key] = await fetch_pharmgkb_evidence(
            gene=gene,
            drug=drug,
            guideline_id=guideline_id,
        )

        # PharmVar
        star_alleles = []

        diplotype = pair.get("diplotype")
        if diplotype:
            for allele in diplotype.split("/"):
                if allele:
                    star_alleles.append(allele.strip())

        if star_alleles:
            pharmvar_results[key] = (
                await pharmvar_service.get_allele_definitions(
                    gene=gene,
                    star_alleles=star_alleles,
                )
            )
        else:
            pharmvar_results[key] = []

        # DrugBank
        drugbank_results[key] = await fetch_drugbank_context(
            drug=drug
        )

    # ---------------------------------------------------------
    # 7. Aggregate all evidence
    # ---------------------------------------------------------

    evidence_packages = aggregate_multiple_evidence(
        matched_pairs=matched_pairs,
        cpic_results=cpic_results,
        pharmgkb_results=pharmgkb_results,
        pharmvar_results=pharmvar_results,
        drugbank_results=drugbank_results,
    )

    # ---------------------------------------------------------
    # 8. Detect conflicts
    # ---------------------------------------------------------

    conflict_results = detect_multiple_conflicts(
        evidence_packages=evidence_packages
    )

    # ---------------------------------------------------------
    # 9. Generate rule-based recommendations
    # ---------------------------------------------------------

    recommendations = build_recommendations(
        evidence_packages=evidence_packages,
        conflict_results=conflict_results,
    )

    # ---------------------------------------------------------
    # 10. Attach complete evidence to recommendations
    # ---------------------------------------------------------

    for recommendation in recommendations:
        gene = recommendation.get("gene")
        drug = recommendation.get("drug")

        matching_evidence = next(
            (
                evidence
                for evidence in evidence_packages
                if evidence.get("gene_drug_pair", {}).get("gene") == gene
                and evidence.get("gene_drug_pair", {}).get("drug") == drug
            ),
            None,
        )

        if matching_evidence:
            recommendation["evidence"] = {
                "cpic": matching_evidence.get("cpic"),
                "pharmgkb": matching_evidence.get("pharmgkb"),
                "pharmvar": matching_evidence.get("pharmvar"),
                "drugbank": matching_evidence.get("drugbank"),
            }

    # ---------------------------------------------------------
    # 11. Calculate engineering confidence
    # ---------------------------------------------------------

    confidence = calculate_confidence(
        recommendations=recommendations
    )

    # ---------------------------------------------------------
    # 12. Generate AI explanations
    # ---------------------------------------------------------

    for recommendation in recommendations:
        explanation = await explain_recommendation(
            recommendation
        )

        recommendation["explanation"] = explanation

    # ---------------------------------------------------------
    # 13. Collect flagged conflicts
    # ---------------------------------------------------------

    flagged_conflicts = []

    for result in conflict_results:
        if result.get("conflict") or result.get("requires_review"):
            flagged_conflicts.append(result)

    # ---------------------------------------------------------
    # 14. Return complete Module 5 result
    # ---------------------------------------------------------

    return {
        "pharmacogene_variants": pharmacogene_variants,
        "diplotypes": diplotype_results,
        "phenotypes": phenotype_results,
        "matched_pairs": matched_pairs,
        "evidence": evidence_packages,
        "recommendations": recommendations,
        "flagged_conflicts": flagged_conflicts,
        "confidence": confidence,
    }
