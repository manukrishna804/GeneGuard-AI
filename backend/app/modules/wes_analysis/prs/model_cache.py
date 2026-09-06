from typing import Dict

from .model_registry import PRS_MODELS
from .pgs_model import load_pgs_model


_MODEL_CACHE: Dict[str, dict] = {}


def get_prs_model(disease: str) -> dict:
    """
    Return a cached PGS model for a disease.

    The model files are static, so they are loaded once and
    reused across requests.
    """

    if disease not in PRS_MODELS:
        raise KeyError(
            f"No PRS model configured for disease: {disease}"
        )

    if disease not in _MODEL_CACHE:
        config = PRS_MODELS[disease]

        _MODEL_CACHE[disease] = load_pgs_model(
            str(config["path"]),
            max_variants=config.get(
                "development_limit"
            ),
        )

    return _MODEL_CACHE[disease]


def clear_model_cache() -> None:
    """
    Clear the in-memory model cache.

    Useful for development/testing when a PGS file changes.
    """

    _MODEL_CACHE.clear()