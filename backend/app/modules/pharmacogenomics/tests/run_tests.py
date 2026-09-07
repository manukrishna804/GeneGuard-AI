import asyncio
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(Path.cwd()))

from app.modules.pharmacogenomics.services.diplotype_caller import (
    call_diplotype_for_gene,
    call_all_diplotypes,
    match_variant_to_star_allele
)
from app.modules.pharmacogenomics.services.phenotype_mapper import (
    calculate_activity_score,
    map_diplotype_to_phenotype
)
from app.modules.pharmacogenomics.services.conflict_detector import evaluate_evidence_conflict
from app.modules.pharmacogenomics.services.pipeline import run_pgx_pipeline


def test_diplotypes():
    print("Testing diplotype caller...")
    v1 = {"gene": "CYP2C19", "rsid": "rs4244285", "hgvs_c": "c.681G>A"}
    assert match_variant_to_star_allele("CYP2C19", v1) == "*2"
    
    v2 = {"gene": "CYP2C19", "rsid": "rs12248560", "hgvs_c": "c.-806C>T"}
    assert match_variant_to_star_allele("CYP2C19", v2) == "*17"

    vars_homo = [{"gene": "CYP2C19", "rsid": "rs4244285", "zygosity": "homozygous_alt"}]
    res = call_diplotype_for_gene("CYP2C19", vars_homo)
    assert res["diplotype"] == "*2/*2"

    vars_het = [{"gene": "CYP2C19", "rsid": "rs4244285", "zygosity": "heterozygous"}]
    res = call_diplotype_for_gene("CYP2C19", vars_het)
    assert res["diplotype"] == "*1/*2"

    vars_hla = [{"gene": "HLA-B", "star_allele": "*57:01"}]
    res_hla = call_diplotype_for_gene("HLA-B", vars_hla)
    assert res_hla["is_risk_positive"] is True

    vars_vk = [{"gene": "VKORC1", "rsid": "rs9923231", "zygosity": "homozygous"}]
    res_vk = call_diplotype_for_gene("VKORC1", vars_vk)
    assert res_vk["diplotype"] == "-1639A/A"

    print("✅ Diplotype caller tests PASSED.")


def test_phenotypes():
    print("Testing phenotype mapper...")
    assert calculate_activity_score("CYP2C19", "*1", "*1") == 2.0
    assert calculate_activity_score("CYP2C19", "*2", "*2") == 0.0
    assert calculate_activity_score("CYP2D6", "*1", "*4") == 1.0

    res_pm = map_diplotype_to_phenotype("CYP2C19", {"diplotype": "*2/*2", "allele1": "*2", "allele2": "*2"})
    assert res_pm["phenotype"] == "Poor Metabolizer"
    assert res_pm["activity_score"] == 0.0

    res_rm = map_diplotype_to_phenotype("CYP2C19", {"diplotype": "*1/*17", "allele1": "*1", "allele2": "*17"})
    assert res_rm["phenotype"] == "Rapid Metabolizer"

    res_d6_pm = map_diplotype_to_phenotype("CYP2D6", {"diplotype": "*4/*4", "allele1": "*4", "allele2": "*4"})
    assert res_d6_pm["phenotype"] == "Poor Metabolizer"

    print("✅ Phenotype mapper tests PASSED.")


def test_conflicts():
    print("Testing conflict detector...")
    evidence_high_risk = {
        "gene_drug_pair": {"drug": "Clopidogrel", "gene": "CYP2C19"},
        "genomic_profile": {"gene": "CYP2C19", "diplotype": "*2/*2", "phenotype": "Poor Metabolizer"},
        "guideline_evidence": {
            "pharmgkb_level": "1A",
            "requires_clinical_review": True,
            "specialist_routing": "Cardiologist / Clinical Pharmacist"
        }
    }
    has_conflict, conflicts, confidence = evaluate_evidence_conflict(evidence_high_risk)
    assert has_conflict is True
    assert len(conflicts) > 0
    assert conflicts[0]["severity"] == "CRITICAL"
    print("✅ Conflict detector tests PASSED.")


async def test_pipelines():
    print("Testing end-to-end PGx pipelines...")
    
    # 1. Clopidogrel with CYP2C19 *2/*2
    res1 = await run_pgx_pipeline(
        patient_id=1,
        medications=["Plavix"],
        custom_variants=[{"gene": "CYP2C19", "rsid": "rs4244285", "zygosity": "homozygous_alt"}],
        use_latest_wes=False
    )
    assert res1["matched_gene_drug_pairs"] == 1
    rec1 = res1["recommendations"][0]
    assert rec1["drug"] == "Clopidogrel"
    assert rec1["diplotype"] == "*2/*2"
    assert rec1["phenotype"] == "Poor Metabolizer"
    assert "Alternative Recommended" in rec1["actionability"] or "Contraindicated" in rec1["actionability"]

    # 2. Codeine with CYP2D6 *1xN Ultrarapid
    res2 = await run_pgx_pipeline(
        patient_id=2,
        medications=["Codeine"],
        custom_variants=[{"gene": "CYP2D6", "star_allele": "*1xN", "zygosity": "heterozygous"}],
        use_latest_wes=False
    )
    rec2 = res2["recommendations"][0]
    assert rec2["phenotype"] == "Ultrarapid Metabolizer"
    assert "Toxicity" in rec2["actionability"] or "Contraindicated" in rec2["actionability"]

    # 3. Abacavir with HLA-B*57:01
    res3 = await run_pgx_pipeline(
        patient_id=3,
        medications=["Abacavir"],
        custom_variants=[{"gene": "HLA-B", "star_allele": "*57:01"}],
        use_latest_wes=False
    )
    rec3 = res3["recommendations"][0]
    assert "High Risk" in rec3["phenotype"]

    # 4. Multi-medication ranking
    res4 = await run_pgx_pipeline(
        patient_id=4,
        medications=["Simvastatin", "Warfarin"],
        custom_variants=[{"gene": "SLCO1B1", "rsid": "rs4149056", "zygosity": "homozygous_alt"}],
        use_latest_wes=False
    )
    assert len(res4["recommendations"]) == 2
    assert res4["recommendations"][0]["drug"] == "Simvastatin"

    print("✅ End-to-end PGx pipeline tests PASSED.")


async def main():
    test_diplotypes()
    test_phenotypes()
    test_conflicts()
    await test_pipelines()
    print("\n🎉 ALL PHARMACOGENOMICS TESTS PASSED SUCCESSFULLY! 🚀")


if __name__ == "__main__":
    asyncio.run(main())
