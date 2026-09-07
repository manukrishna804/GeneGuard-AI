# Module 5: Pharmacogenomics (PGx) Clinical Decision Support Engine

## Overview
Module 5 provides a deterministic, evidence-graded clinical decision support (CDS) engine that translates patient genomic variation (from WES/VCF analysis) and current medication lists into actionable drug efficacy, dosing, and safety recommendations.

The module strictly follows established clinical guidelines (**CPIC**, **PharmGKB / ClinPGx**, **PharmVar**, **FDA PGx Biomarkers**, and **DrugBank**) using a 12-stage rule-based architecture.

## 12-Stage Pipeline Architecture
1. **Stage 1 (Input)**: Ingests genomic variants from WES report / Module 1 or direct JSON, plus prescribed medication list.
2. **Stage 2 (Pharmacogene Filter)**: Filters for established pharmacogenes (`CYP2D6`, `CYP2C19`, `CYP2C9`, `CYP3A5`, `DPYD`, `TPMT`, `NUDT15`, `SLCO1B1`, `VKORC1`, `HLA-B`, `HLA-A`, `UGT1A1`, `G6PD`).
3. **Stage 3 (Star-Allele / Diplotype Calling)**: Resolves star-alleles (*1, *2, *3, *4, *17, etc.) and diplotypes against PharmVar allele definitions.
4. **Stage 4 (Genotype → Phenotype Mapping)**: Calculates activity scores and maps to CPIC consensus metabolizer phenotypes (Poor, Intermediate, Normal, Rapid, Ultrarapid).
5. **Stage 5 (Drug List Matching)**: Intersects patient drugs (including brand names like Plavix, Coumadin, Lipitor) with known gene-drug pairs.
6. **Stage 6 (Guideline Lookup)**: Parallel async lookups to CPIC, PharmGKB, FDA Table, and DrugBank, with local offline cache fallbacks.
7. **Stage 7 (Evidence Aggregation)**: Merges all multi-source evidence into a master structured JSON.
8. **Stage 8 (Conflict Detection & Confidence Scoring)**: Evaluates evidence concordance, computes 0–100% confidence, and flags records for specialist review.
9. **Stage 9 (Recommendation Ranking)**: Prioritizes recommendations by clinical urgency (Contraindicated > Major Dose Change > Moderate Adjustment > Standard).
10. **Stage 10 (AI Explanation Layer)**: Generates clear patient-friendly and clinician-oriented summaries using LLM (Groq / OpenAI) with deterministic template fallback.
11. **Stage 11 (Structured Output)**: Emits `pgx_recommendations.json` payload for downstream consumption by Module 6 (Final Integrated Report).
12. **Stage 12 (API & Reporting Integration)**: FastAPI REST endpoints for real-time analysis, query by patient ID, and PDF reporting.

## Key API Endpoints
- `POST /api/v1/pharmacogenomics/analyze`: Run full PGx analysis for a patient and medication list.
- `GET /api/v1/pharmacogenomics/patient/{patient_id}/reports`: Retrieve all historical PGx reports for a patient.
- `GET /api/v1/pharmacogenomics/report/{report_id}`: Retrieve a specific report by ID.
- `GET /api/v1/pharmacogenomics/supported-drugs`: Search supported medications and brand names.
- `GET /api/v1/pharmacogenomics/supported-genes`: List covered pharmacogenes and star-allele definitions.
- `GET /api/v1/pharmacogenomics/ping`: Health check.
