
from app.modules.pharmacogenomics.services.diplotype_caller import (
    build_diplotype,
    call_diplotype,
    call_diplotypes,
    normalize_star_allele,
)


def test_normalize_star_allele():
    assert normalize_star_allele(" 2 ") == "*2"
    assert normalize_star_allele("*1") == "*1"


def test_build_diplotype_with_two_alleles():
    assert build_diplotype("CYP2C19", ["*1", "*2"]) == "*1/*2"


def test_build_diplotype_requires_two_alleles():
    assert build_diplotype("CYP2C19", ["*2"]) is None


def test_call_diplotype_without_star_alleles():
    result = call_diplotype("CYP2C19", [{"gene": "CYP2C19"}])
    assert result["status"] == "insufficient_data"
    assert result["diplotype"] is None


def test_call_diplotypes():
    result = call_diplotypes({
        "CYP2C19": [
            {"star_allele": "*1"},
            {"star_allele": "*2"},
        ]
    })
    assert result[0]["diplotype"] == "*1/*2"
    assert result[0]["status"] == "complete"
