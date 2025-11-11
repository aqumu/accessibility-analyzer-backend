from typing import Dict, Any
from app.services.accessibility.base_extractor import BaseExtractor

class RoleExtractor(BaseExtractor):
    """
    Extracts the role of an element along with its HTML tag and text content.
    Useful for analyzing native vs. ARIA roles and context.
    """

    def extract(self, el: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "tag": el.get("tag"),
            "role": el.get("role"),
            "text": (el.get("text") or "").strip()
        }
