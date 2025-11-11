from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseExtractor(ABC):
    """Base interface for all element data extractors."""

    @abstractmethod
    def extract(self, el: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts data from one element dict."""
        pass

    def filter(self, el: Dict[str, Any]) -> bool:
        """Optional filter to decide whether extractor applies to element."""
        return True
