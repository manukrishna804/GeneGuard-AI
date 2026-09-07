import pytest
from app.modules.pharmacogenomics.services.phenotype_mapper import (
    calculate_activity_score,
    map_diplotype_to_phenotype
)


def test_activity_score_calculation():
    # CYP2C19 *1/*1 -> 1.0 + 1.0 = 2.0
    assert calculate_activity_score("CYP2C19", "*1", "*1") == 2.0

    # CYP2C19 *2/*2 -> 0.0 + 0.0 = 0.0
    assert calculate_activity_score("CYP2C19", "*2", "*2") == 0.0

    # CYP2D6 *1/*4 -> 1.0 + 0.0 = 1.0
    assert calculate_activity_score("CYP2D6", "*1", "*4") == 1.0

    # CYP2D6 *1xN/*1 -> 2.0 + 1.0 = 3.0
    assert calculate_activity_score("CYP2D6", "*1xN", "*1") == 3.0


def test_cyp2c19_phenotype_mapping():
    # *2/*2 -> Poor Metabolizer
    res_pm = map_diplotype_to_phenotype("CYP2C19", {"diplotype": "*2/*2", "allele1": "*2", "allele2": "*2"})
    assert res_pm["phenotype"] == "Poor Metabolizer"
    assert res_pm["activity_score"] == 0.0

    # *1/*17 -> Rapid Metabolizer
    res_rm = map_diplotype_to_phenotype("CYP2C19", {"diplotype": "*1/*17", "allele1": "*1", "allele2": "*17"})
    assert res_rm["phenotype"] == "Rapid Metabolizer"
    assert res_rm["activity_score"] == 2.5


def test_cyp2d6_phenotype_mapping():
    # *4/*4 -> Poor Metabolizer
    res_pm = map_diplotype_to_phenotype("CYP2D6", {"diplotype": "*4/*4", "allele1": "*4", "allele2": "*4"})
    assert res_pm["phenotype"] == "Poor Metabolizer"

    # *1xN/*1 -> Ultrarapid Metabolizer
    res_um = map_diplotype_to_phenotype("CYP2D6", {"diplotype": "*1xN/*1", "allele1": "*1xN", "allele2": "*1"})
    assert res_um["phenotype"] == "Ultrarapid Metabolizer"


def test_hlab_phenotype_mapping():
    # HLA-B*57:01 positive
    res_hla = map_diplotype_to_phenotype("HLA-B", {
        "diplotype": "*57:01 (Positive)",
        "allele1": "*57:01",
        "is_risk_positive": True
    })
    assert "Abacavir Hypersensitivity High Risk" in res_hla["phenotype"]
    assert res_hla["phenotype_code"] == "POS"
