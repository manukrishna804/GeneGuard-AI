import pytest
from app.modules.pharmacogenomics.services.pipeline import run_pgx_pipeline


@pytest.mark.asyncio
async def test_clopidogrel_cyp2c19_pipeline():
    # Patient taking Plavix (Clopidogrel) with homozygous CYP2C19 *2 variant
    variants = [
        {"gene": "CYP2C19", "rsid": "rs4244285", "zygosity": "homozygous_alt"}
    ]
    meds = ["Plavix"]

    res = await run_pgx_pipeline(
        patient_id=1,
        medications=meds,
        custom_variants=variants,
        use_latest_wes=False
    )

    assert res["patient_id"] == 1
    assert res["matched_gene_drug_pairs"] == 1
    assert len(res["recommendations"]) == 1

    rec = res["recommendations"][0]
    assert rec["drug"] == "Clopidogrel"
    assert rec["gene"] == "CYP2C19"
    assert rec["diplotype"] == "*2/*2"
    assert rec["phenotype"] == "Poor Metabolizer"
    assert "Alternative Recommended" in rec["actionability"] or "Contraindicated" in rec["actionability"]
    assert "Avoid clopidogrel" in rec["recommendation"]
    assert rec["patient_explanation"] != ""
    assert rec["clinician_summary"] != ""


@pytest.mark.asyncio
async def test_codeine_cyp2d6_ultrarapid_pipeline():
    # Patient taking Codeine with CYP2D6 gene duplication (*1xN)
    variants = [
        {"gene": "CYP2D6", "star_allele": "*1xN", "zygosity": "heterozygous"}
    ]
    meds = ["Codeine"]

    res = await run_pgx_pipeline(
        patient_id=2,
        medications=meds,
        custom_variants=variants,
        use_latest_wes=False
    )

    rec = res["recommendations"][0]
    assert rec["drug"] == "Codeine"
    assert rec["gene"] == "CYP2D6"
    assert rec["phenotype"] == "Ultrarapid Metabolizer"
    assert "Toxicity" in rec["actionability"] or "Contraindicated" in rec["actionability"]


@pytest.mark.asyncio
async def test_abacavir_hlab_pipeline():
    # Patient taking Abacavir with HLA-B*57:01
    variants = [
        {"gene": "HLA-B", "star_allele": "*57:01"}
    ]
    meds = ["Abacavir"]

    res = await run_pgx_pipeline(
        patient_id=3,
        medications=meds,
        custom_variants=variants,
        use_latest_wes=False
    )

    rec = res["recommendations"][0]
    assert rec["drug"] == "Abacavir"
    assert "High Risk" in rec["phenotype"]
    assert "Contraindicated" in rec["actionability"]


@pytest.mark.asyncio
async def test_multi_medication_ranking_pipeline():
    # Patient taking Simvastatin (*5/*5) and standard Warfarin (*1/*1)
    variants = [
        {"gene": "SLCO1B1", "rsid": "rs4149056", "zygosity": "homozygous_alt"}
    ]
    meds = ["Simvastatin", "Warfarin"]

    res = await run_pgx_pipeline(
        patient_id=4,
        medications=meds,
        custom_variants=variants,
        use_latest_wes=False
    )

    assert len(res["recommendations"]) >= 2
    # Simvastatin (*5/*5 has high risk rank 1 or 2) should rank before standard Warfarin
    assert res["recommendations"][0]["drug"] == "Simvastatin"
    assert res["recommendations"][0]["rank_priority"] <= res["recommendations"][1]["rank_priority"]
