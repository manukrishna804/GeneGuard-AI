
import pytest

from app.modules.pharmacogenomics.services.vcf_parser import (
    VCFParseError,
    parse_vcf_content,
)


def test_parse_valid_vcf():
    content = (
        "##fileformat=VCFv4.2\n"
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
        "1\t10001\trsTEST001\tA\tG\t.\tPASS\t.\n"
    ).encode("utf-8")

    variants = parse_vcf_content(content)

    assert len(variants) == 1
    assert variants[0]["chromosome"] == "1"
    assert variants[0]["position"] == 10001
    assert variants[0]["rsid"] == "rsTEST001"
    assert variants[0]["reference"] == "A"
    assert variants[0]["alternate"] == "G"


def test_reject_missing_chrom_header():
    content = b"This is not a valid VCF file."

    with pytest.raises(VCFParseError, match="#CHROM"):
        parse_vcf_content(content)


def test_reject_empty_file():
    with pytest.raises(VCFParseError, match="empty"):
        parse_vcf_content(b"")

def test_parse_sample_genotype():
    content = (
        "##fileformat=VCFv4.2\n"
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE1\n"
        "10\t20002\trsTEST002\tC\tT\t.\tPASS\t.\tGT:DP\t1/1:30\n"
    ).encode("utf-8")

    variants = parse_vcf_content(content)

    assert len(variants) == 1
    assert variants[0]["genotype"] == "1/1"
    assert variants[0]["alternate"] == "T"


def test_parse_multiple_alternate_alleles():
    content = (
        "##fileformat=VCFv4.2\n"
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
        "1\t10001\trsTEST003\tA\tG,T\t.\tPASS\t.\n"
    ).encode("utf-8")

    variants = parse_vcf_content(content)

    assert len(variants) == 2
    assert [variant["alternate"] for variant in variants] == ["G", "T"]
