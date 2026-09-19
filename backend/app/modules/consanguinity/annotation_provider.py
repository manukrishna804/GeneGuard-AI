from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .schemas import GeneticVariant


class AnnotationProvider(ABC):
    """
    Base interface for variant annotation sources.
    """

    @abstractmethod
    def annotate(self, variant: GeneticVariant) -> Optional[GeneticVariant]:
        """
        Annotate a variant and return the updated variant.

        Return None if the provider has no annotation.
        """
        raise NotImplementedError


class LocalAnnotationProvider(AnnotationProvider):
    """
    Simple local provider used for development/testing.
    """

    def annotate(self, variant: GeneticVariant) -> Optional[GeneticVariant]:
        return None