from typing import Dict, Any
from app.services.accessibility.base_extractor import BaseExtractor

class AriaExtractor(BaseExtractor):
    """
    Extracts all ARIA attributes from an element.
    Returns a dictionary of aria-* attributes.
    """

    def filter(self, el: Dict[str, Any]) -> bool:
        # Only run if the element actually has aria attributes
        return bool(el.get("aria"))

    def extract(self, el: Dict[str, Any]) -> Dict[str, Any]:
        aria = el.get("aria", {})
        return {"aria_attributes": aria}
