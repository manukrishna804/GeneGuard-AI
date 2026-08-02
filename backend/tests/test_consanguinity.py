"""
Tests for app.api.v1.endpoints.consanguinity

These call the endpoint function directly (no DB dependency, since the
consanguinity module is intentionally stateless) rather than spinning up a
full TestClient -- matches how tests/test_genetics_engine.py tests the
underlying engine directly. Values are cross-checked against the same
punnett_square() cases already covered there, to confirm this endpoint is a
correct, thin wrapper around the shared engine and not a second, drifting
implementation.
"""
import pytest

from app.api.v1.endpoints.consanguinity import (
    assess_consanguinity_risk,
    ConsanguinityRequest,
)
from app.services.genetics_engine import CarrierStatus, InheritanceMode


def _request(**overrides) -> ConsanguinityRequest:
    defaults = dict(
        condition_name="Beta-thalassemia",
        parent1_status=CarrierStatus.CARRIER,
        parent2_status=CarrierStatus.CARRIER,
        inheritance_mode=InheritanceMode.AUTOSOMAL_RECESSIVE,
        relationship_type=None,
    )
    defaults.update(overrides)
    return ConsanguinityRequest(**defaults)


def test_two_carriers_returns_25_50_25():
    result = assess_consanguinity_risk(_request())
    assert result.probabilities == {"affected": 0.25, "carrier": 0.50, "unaffected": 0.25}


def test_one_carrier_one_unaffected_gives_no_affected_risk():
    result = assess_consanguinity_risk(_request(
        parent1_status=CarrierStatus.CARRIER,
        parent2_status=CarrierStatus.UNAFFECTED,
    ))
    assert result.probabilities["affected"] == 0.0
    assert result.probabilities["carrier"] == 0.5
    assert result.probabilities["unaffected"] == 0.5


def test_two_affected_parents_gives_all_affected():
    result = assess_consanguinity_risk(_request(
        parent1_status=CarrierStatus.AFFECTED,
        parent2_status=CarrierStatus.AFFECTED,
    ))
    assert result.probabilities["affected"] == 1.0


def test_response_echoes_condition_and_mode():
    result = assess_consanguinity_risk(_request(condition_name="Cystic Fibrosis"))
    assert result.condition_name == "Cystic Fibrosis"
    assert result.inheritance_mode == InheritanceMode.AUTOSOMAL_RECESSIVE.value


def test_relationship_type_is_echoed_but_does_not_change_probabilities():
    """
    Relationship type (e.g. first cousin) is contextual only -- it must not
    alter the Punnett-square math itself, only the explanation text. This
    guards against a future change accidentally folding relationship type
    into the probability calculation, which would be biologically incorrect
    (consanguinity affects the CHANCE both parents are carriers, not the
    offspring probabilities once carrier status is already known).
    """
    with_relation = assess_consanguinity_risk(_request(relationship_type="first_cousin"))
    without_relation = assess_consanguinity_risk(_request(relationship_type=None))

    assert with_relation.probabilities == without_relation.probabilities
    assert with_relation.relationship_type == "first_cousin"
    assert without_relation.relationship_type is None


def test_relationship_type_note_appears_in_explanation_when_provided():
    result = assess_consanguinity_risk(_request(relationship_type="first_cousin"))
    assert "first_cousin" in result.explanation
    assert "counselor" in result.explanation.lower()


def test_unrelated_relationship_type_does_not_add_consanguinity_note():
    result = assess_consanguinity_risk(_request(relationship_type="unrelated"))
    assert "statistically more likely" not in result.explanation


def test_explanation_always_includes_disclaimer():
    result = assess_consanguinity_risk(_request())
    assert "not a diagnosis" in result.explanation.lower()


def test_dominant_mode_matches_engine_directly():
    """Sanity check against InheritanceMode.AUTOSOMAL_DOMINANT, not just the default recessive path."""
    result = assess_consanguinity_risk(_request(
        parent1_status=CarrierStatus.AFFECTED,
        parent2_status=CarrierStatus.UNAFFECTED,
        inheritance_mode=InheritanceMode.AUTOSOMAL_DOMINANT,
    ))
    assert result.probabilities["affected"] == 0.50
    assert result.probabilities["unaffected"] == 0.50