import pytest
from app.modules.pharmacogenomics.services.diplotype_caller import (
    call_diplotype_for_gene,
    call_all_diplotypes,
    match_variant_to_star_allele
)


def test_cyp2c19_star_allele_matching():
    # Test rs4244285 -> *2
    v1 = {"gene": "CYP2C19", "rsid": "rs4244285", "hgvs_c": "c.681G>A"}
    assert match_variant_to_star_allele("CYP2C19", v1) == "*2"

    # Test rs12248560 -> *17
    v2 = {"gene": "CYP2C19", "rsid": "rs12248560", "hgvs_c": "c.-806C>T"}
    assert match_variant_to_star_allele("CYP2C19", v2) == "*17"


def test_cyp2c19_homozygous_diplotype_calling():
    # Homozygous *2 -> *2/*2
    vars_homo = [{"gene": "CYP2C19", "rsid": "rs4244285", "zygosity": "homozygous_alt"}]
    res = call_diplotype_for_gene("CYP2C19", vars_homo)
    assert res["diplotype"] == "*2/*2"
    assert res["allele1"] == "*2"
    assert res["allele2"] == "*2"


def test_cyp2c19_heterozygous_diplotype_calling():
    # Heterozygous *2 -> *1/*2
    vars_het = [{"gene": "CYP2C19", "rsid": "rs4244285", "zygosity": "heterozygous"}]
    res = call_diplotype_for_gene("CYP2C19", vars_het)
    assert res["diplotype"] == "*1/*2"
    assert res["allele1"] == "*1"
    assert res["allele2"] == "*2"


def test_cyp2d6_diplotype_calling():
    # CYP2D6 *4 heterozygous -> *1/*4
    vars_d6 = [{"gene": "CYP2D6", "rsid": "rs3892097", "zygosity": "heterozygous"}]
    res = call_diplotype_for_gene("CYP2D6", vars_d6)
    assert res["diplotype"] == "*1/*4"


def test_hlab_risk_allele_calling():
    # HLA-B*57:01 positive
    vars_hla = [{"gene": "HLA-B", "star_allele": "*57:01"}]
    res = call_diplotype_for_gene("HLA-B", vars_hla)
    assert res["is_risk_positive"] is True
    assert "*57:01" in res["diplotype"]

    # HLA-B negative (no variants)
    res_neg = call_diplotype_for_gene("HLA-B", [])
    assert res_neg["is_risk_positive"] is False


def test_vkorc1_diplotype_calling():
    # VKORC1 homozygous A -> -1639A/A
    vars_vk = [{"gene": "VKORC1", "rsid": "rs9923231", "zygosity": "homozygous"}]
    res = call_diplotype_for_gene("VKORC1", vars_vk)
    assert res["diplotype"] == "-1639A/A"
