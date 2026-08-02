"""
Tests for app.services.genetics_engine

Covers:
  - punnett_square() against textbook Mendelian outcomes
  - detect_inheritance_pattern() against known pedigree signatures,
    including the two misclassification cases found during manual review
    (single affected male mistaken for X-linked; a true X-linked pedigree
    mistaken for autosomal dominant) that motivated the rule rewrite.
"""
import pytest

from app.services.genetics_engine import (
    punnett_square,
    detect_inheritance_pattern,
    CarrierStatus,
    InheritanceMode,
    PedigreeNode,
)


# ---------------------------------------------------------------------------
# punnett_square()
# ---------------------------------------------------------------------------

def test_two_carriers_gives_25_50_25():
    result = punnett_square(CarrierStatus.CARRIER, CarrierStatus.CARRIER)
    assert result == {"affected": 0.25, "carrier": 0.50, "unaffected": 0.25}


def test_carrier_and_unaffected_gives_no_affected_risk():
    result = punnett_square(CarrierStatus.CARRIER, CarrierStatus.UNAFFECTED)
    assert result["affected"] == 0.0
    assert result["carrier"] == 0.5
    assert result["unaffected"] == 0.5


def test_two_affected_parents_recessive_gives_all_affected():
    result = punnett_square(CarrierStatus.AFFECTED, CarrierStatus.AFFECTED)
    assert result["affected"] == 1.0


def test_two_unaffected_parents_gives_no_risk():
    result = punnett_square(CarrierStatus.UNAFFECTED, CarrierStatus.UNAFFECTED)
    assert result == {"affected": 0.0, "carrier": 0.0, "unaffected": 1.0}


def test_probabilities_always_sum_to_one():
    statuses = [CarrierStatus.CARRIER, CarrierStatus.AFFECTED,
                CarrierStatus.UNAFFECTED, CarrierStatus.UNKNOWN]
    for p1 in statuses:
        for p2 in statuses:
            result = punnett_square(p1, p2)
            assert abs(sum(result.values()) - 1.0) < 1e-9, (p1, p2, result)


# ---------------------------------------------------------------------------
# detect_inheritance_pattern()
# ---------------------------------------------------------------------------

def test_recessive_single_affected_child_unaffected_parents():
    members = [
        PedigreeNode(member_id=1, sex="M", health_status="Unaffected", parent_id=None),
        PedigreeNode(member_id=2, sex="F", health_status="Unaffected", parent_id=None),
        PedigreeNode(member_id=3, sex="F", health_status="Affected", parent_id=1),
    ]
    result = detect_inheritance_pattern(members)
    assert result["pattern"] == InheritanceMode.AUTOSOMAL_RECESSIVE.value


def test_dominant_three_generation_straight_line():
    members = [
        PedigreeNode(member_id=1, sex="M", health_status="Affected", parent_id=None),
        PedigreeNode(member_id=2, sex="M", health_status="Affected", parent_id=1),
        PedigreeNode(member_id=3, sex="M", health_status="Affected", parent_id=2),
    ]
    result = detect_inheritance_pattern(members)
    assert result["pattern"] == InheritanceMode.AUTOSOMAL_DOMINANT.value
    assert result["confidence"] == "high"


def test_true_xlinked_recessive_pedigree_not_misread_as_dominant():
    """
    Regression test: affected maternal uncle + affected nephew via an
    unaffected (carrier) mother, no affected fathers anywhere. This is a
    textbook X-linked recessive signature. Before the rule rewrite, the
    detector incorrectly labeled this 'autosomal_dominant' because it only
    checked whether affected members spanned >=2 generations.
    """
    members = [
        PedigreeNode(member_id=1, sex="F", health_status="Unaffected", parent_id=None),
        PedigreeNode(member_id=2, sex="M", health_status="Affected", parent_id=1),
        PedigreeNode(member_id=3, sex="F", health_status="Unaffected", parent_id=1),
        PedigreeNode(member_id=4, sex="M", health_status="Affected", parent_id=3),
    ]
    result = detect_inheritance_pattern(members)
    assert result["pattern"] == InheritanceMode.X_LINKED_RECESSIVE.value


def test_father_to_son_transmission_rules_out_xlinked():
    """
    An affected father cannot pass an X-linked recessive condition to a son
    (sons inherit Y, not X, from their father). This case should NOT be
    classified as X-linked recessive.
    """
    members = [
        PedigreeNode(member_id=1, sex="M", health_status="Affected", parent_id=None),
        PedigreeNode(member_id=2, sex="M", health_status="Affected", parent_id=1),
    ]
    result = detect_inheritance_pattern(members)
    assert result["pattern"] != InheritanceMode.X_LINKED_RECESSIVE.value
    assert result["pattern"] == InheritanceMode.AUTOSOMAL_DOMINANT.value


def test_recessive_affected_siblings_mixed_sex():
    members = [
        PedigreeNode(member_id=1, sex="M", health_status="Unaffected", parent_id=None),
        PedigreeNode(member_id=2, sex="F", health_status="Unaffected", parent_id=None),
        PedigreeNode(member_id=3, sex="M", health_status="Affected", parent_id=1),
        PedigreeNode(member_id=4, sex="F", health_status="Affected", parent_id=1),
    ]
    result = detect_inheritance_pattern(members)
    assert result["pattern"] == InheritanceMode.AUTOSOMAL_RECESSIVE.value
    assert result["confidence"] == "high"


def test_single_affected_member_with_no_data_is_unknown_not_a_guess():
    """
    Regression test: a lone affected member with no parent information at
    all was previously mislabeled 'x_linked_recessive' with 'moderate'
    confidence, purely because they happened to be male. There is no real
    evidence for any specific pattern here -- the detector should say so.
    """
    members = [
        PedigreeNode(member_id=1, sex="M", health_status="Affected", parent_id=None),
    ]
    result = detect_inheritance_pattern(members)
    assert result["pattern"] == InheritanceMode.UNKNOWN.value
    assert result["confidence"] == "low"


def test_no_affected_members_returns_unknown():
    members = [
        PedigreeNode(member_id=1, sex="M", health_status="Unaffected", parent_id=None),
        PedigreeNode(member_id=2, sex="F", health_status="Unaffected", parent_id=None),
    ]
    result = detect_inheritance_pattern(members)
    assert result["pattern"] == InheritanceMode.UNKNOWN.value
    assert result["affected_count"] == 0


def test_empty_pedigree_returns_unknown():
    result = detect_inheritance_pattern([])
    assert result["pattern"] == InheritanceMode.UNKNOWN.value