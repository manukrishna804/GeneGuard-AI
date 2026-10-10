
from app.modules.pharmacogenomics.services import variant_annotator


class MockResponse:
    status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return {
            "dbnsfp": {
                "genename": ["CYP2C19"]
            }
        }


def test_annotate_variant_success(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(variant_annotator.requests, "get", mock_get)

    result = variant_annotator.annotate_variant(
        chromosome="10",
        position=96521657,
        reference="G",
        alternate="A",
    )

    assert result["status"] == "success"
    assert result["assembly"] == "GRCh38"
    assert result["gene"] == "CYP2C19"


def test_annotate_variant_invalid_position():
    result = variant_annotator.annotate_variant(
        chromosome="10",
        position=0,
        reference="G",
        alternate="A",
    )

    assert result["status"] == "error"


def test_annotate_variant_not_found(monkeypatch):
    class NotFoundResponse:
        status_code = 404

    def mock_get(*args, **kwargs):
        return NotFoundResponse()

    monkeypatch.setattr(variant_annotator.requests, "get", mock_get)

    result = variant_annotator.annotate_variant(
        chromosome="10",
        position=96521657,
        reference="G",
        alternate="A",
    )

    assert result["status"] == "not_found"
