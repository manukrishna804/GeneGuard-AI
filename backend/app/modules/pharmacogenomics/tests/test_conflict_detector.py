import pytest
from app.modules.pharmacogenomics.services.conflict_detector import evaluate_evidence_conflict


def test_conflict_detection_high_risk_drug():
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
    assert "Cardiologist / Clinical Pharmacist" in conflicts[0]["action"]


def test_conflict_detection_indeterminate_phenotype():
    evidence_ind = {
        "gene_drug_pair": {"drug": "Codeine", "gene": "CYP2D6"},
        "genomic_profile": {"gene": "CYP2D6", "diplotype": "*unknown", "phenotype": "Indeterminate Metabolizer"},
        "guideline_evidence": {
            "pharmgkb_level": "1A",
            "requires_clinical_review": False
        }
    }

    has_conflict, conflicts, confidence = evaluate_evidence_conflict(evidence_ind)
    assert has_conflict is True
    assert confidence < 90.0
    assert any(c["type"] == "indeterminate_phenotype" for c in conflicts)
