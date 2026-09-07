import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx

try:
    from sqlalchemy.orm import Session
    from app.modules.pharmacogenomics.model import PGxReport
    from app.modules.wes_analysis.model import WESReport
except ImportError:
    Session = Any
    PGxReport = None
    WESReport = None

from app.modules.pharmacogenomics.schema import DiplotypeCall, GeneDrugRecommendation, PGxPipelineResponse
from app.modules.pharmacogenomics.services.pharmacogene_filter import filter_pharmacogene_variants
from app.modules.pharmacogenomics.services.diplotype_caller import call_all_diplotypes
from app.modules.pharmacogenomics.services.phenotype_mapper import map_all_diplotypes_to_phenotypes
from app.modules.pharmacogenomics.services.drug_matcher import match_medications_to_genes
from app.modules.pharmacogenomics.services.guideline_fetcher import fetch_guidelines_for_pair
from app.modules.pharmacogenomics.services.evidence_aggregator import aggregate_gene_drug_evidence
from app.modules.pharmacogenomics.services.conflict_detector import evaluate_evidence_conflict
from app.modules.pharmacogenomics.services.recommendation_ranker import rank_recommendations
from app.modules.pharmacogenomics.services.ai_explainer import generate_ai_explanations


def extract_variants_from_wes(db: Any, patient_id: int) -> List[Dict[str, Any]]:
    """
    Extract variant records from the patient's latest completed WES analysis report.
    """
    if not db or not WESReport:
        return []
    latest_wes = (
        db.query(WESReport)
        .filter(WESReport.patient_id == patient_id)
        .order_by(WESReport.created_at.desc())
        .first()
    )
    
    if not latest_wes or not latest_wes.analysis_result:
        return []
        
    extracted_variants = []
    for item in latest_wes.analysis_result:
        if isinstance(item, dict):
            var_data = item.get("variant") or item
            extracted_variants.append(var_data)
            
    return extracted_variants


async def run_pgx_pipeline(
    patient_id: int,
    medications: List[str],
    custom_variants: Optional[List[Dict[str, Any]]] = None,
    db: Optional[Session] = None,
    use_latest_wes: bool = True
) -> Dict[str, Any]:
    """
    Master Execution Pipeline for GeneGuard Module 5: Pharmacogenomics CDS Engine.
    Executes Stages 1 through 11.
    """
    # ----------------------------------------------------
    # STAGE 1: INGEST VARIANTS & MEDICATIONS
    # ----------------------------------------------------
    raw_variants: List[Dict[str, Any]] = []
    
    if custom_variants:
        raw_variants.extend(custom_variants)
    elif db and use_latest_wes:
        wes_vars = extract_variants_from_wes(db, patient_id)
        raw_variants.extend(wes_vars)

    # ----------------------------------------------------
    # STAGE 2: PHARMACOGENE FILTER
    # ----------------------------------------------------
    filtered_variants = filter_pharmacogene_variants(raw_variants)

    # ----------------------------------------------------
    # STAGE 5 (A): MATCH DRUGS TO PHARMACOGENES
    # ----------------------------------------------------
    matched_pairs, unmatched_drugs = match_medications_to_genes(medications)
    
    # Target genes needed for the patient's drugs
    target_genes = list({pair["primary_gene"] for pair in matched_pairs})

    # ----------------------------------------------------
    # STAGE 3: STAR-ALLELE / DIPLOTYPE CALLING
    # ----------------------------------------------------
    diplotype_calls_raw = call_all_diplotypes(filtered_variants, target_genes=target_genes)

    # ----------------------------------------------------
    # STAGE 4: GENOTYPE -> PHENOTYPE MAPPING
    # ----------------------------------------------------
    phenotype_map = map_all_diplotypes_to_phenotypes(diplotype_calls_raw)

    # ----------------------------------------------------
    # STAGE 6, 7, 8, 9, 10: PER-PAIR EVIDENCE & RECOMMENDATIONS
    # ----------------------------------------------------
    all_recommendations: List[Dict[str, Any]] = []
    all_conflicts: List[Dict[str, Any]] = []
    all_evidence_packages: List[Dict[str, Any]] = []
    confidence_accumulator: List[float] = []

    async with httpx.AsyncClient() as http_client:
        for pair in matched_pairs:
            drug = pair["drug_name"]
            gene = pair["primary_gene"]
            diplotype_info = phenotype_map.get(gene, {
                "gene": gene,
                "diplotype": "*1/*1",
                "allele1": "*1",
                "allele2": "*1",
                "phenotype": "Normal Metabolizer",
                "phenotype_code": "NM",
                "activity_score": 2.0
            })
            phenotype = diplotype_info["phenotype"]

            # Stage 6: Guideline fetch
            guidelines = await fetch_guidelines_for_pair(drug, gene, phenotype, client=http_client)

            # Stage 7: Evidence aggregation
            evidence = aggregate_gene_drug_evidence(pair, diplotype_info, guidelines)
            all_evidence_packages.append(evidence)

            # Stage 8: Conflict detection
            has_conflict, conflicts, pair_confidence = evaluate_evidence_conflict(evidence)
            if conflicts:
                all_conflicts.extend(conflicts)
            confidence_accumulator.append(pair_confidence)

            # Stage 10: AI Explanation Layer (or fallback)
            explanations = await generate_ai_explanations(evidence)

            rec_item = {
                "drug": drug,
                "gene": gene,
                "diplotype": diplotype_info.get("diplotype", "*1/*1"),
                "phenotype": phenotype,
                "activity_score": diplotype_info.get("activity_score"),
                "actionability": guidelines.get("actionability", "Standard Dosing"),
                "recommendation": guidelines.get("recommendation", "Standard dosing."),
                "clinical_implication": guidelines.get("clinical_implication", "Normal response expected."),
                "evidence_level": guidelines.get("evidence_level", "CPIC Level A"),
                "pharmgkb_level": guidelines.get("pharmgkb_level", "1A"),
                "source": guidelines.get("source", "CPIC Guidelines"),
                "fda_label_status": pair.get("fda_label_status"),
                "conflict": has_conflict,
                "conflict_details": (conflicts[0]["message"] if conflicts else None),
                "requires_specialist_review": guidelines.get("requires_review", False) or has_conflict,
                "specialist": guidelines.get("specialist", "Clinical Pharmacist"),
                "patient_explanation": explanations.get("patient_explanation", ""),
                "clinician_summary": explanations.get("clinician_summary", "")
            }

            all_recommendations.append(rec_item)

    # Stage 9: Recommendation ranking
    ranked_recommendations = rank_recommendations(all_recommendations)

    overall_confidence = (
        round(sum(confidence_accumulator) / len(confidence_accumulator), 1)
        if confidence_accumulator else 95.0
    )

    # ----------------------------------------------------
    # STAGE 11: STRUCTURED OUTPUT PACKAGE
    # ----------------------------------------------------
    status = "flagged_for_review" if len(all_conflicts) > 0 else "completed"
    
    # Format DiplotypeCall list for response
    diplotype_response_list = [
        DiplotypeCall(
            gene=g,
            diplotype=d.get("diplotype", "*1/*1"),
            activity_score=d.get("activity_score"),
            phenotype=d.get("phenotype", "Normal Metabolizer"),
            phenotype_code=d.get("phenotype_code"),
            evidence_alleles=d.get("evidence_alleles", []),
            source=d.get("source", "CPIC / PharmVar")
        )
        for g, d in phenotype_map.items()
    ]

    response_payload = {
        "patient_id": patient_id,
        "timestamp": datetime.utcnow(),
        "status": status,
        "total_drugs_evaluated": len(medications),
        "matched_gene_drug_pairs": len(matched_pairs),
        "overall_confidence": overall_confidence,
        "flagged_conflicts": all_conflicts,
        "diplotype_calls": diplotype_response_list,
        "recommendations": ranked_recommendations,
        "unmatched_drugs": unmatched_drugs,
        "full_evidence_package": all_evidence_packages
    }

    # ----------------------------------------------------
    # DATABASE PERSISTENCE (Optional if db provided)
    # ----------------------------------------------------
    report_id = None
    if db:
        try:
            report_record = PGxReport(
                patient_id=patient_id,
                status=status,
                confidence_score=overall_confidence,
                flagged_conflicts_count=len(all_conflicts),
                medications_evaluated=medications,
                recommendations=[
                    {k: v for k, v in r.items()} for r in ranked_recommendations
                ],
                full_evidence_package=all_evidence_packages
            )
            db.add(report_record)
            db.commit()
            db.refresh(report_record)
            report_id = report_record.id
            response_payload["report_id"] = report_id
        except Exception:
            db.rollback()

    return response_payload
