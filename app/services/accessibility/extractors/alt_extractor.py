from typing import Dict, Any
from app.services.accessibility.base_extractor import BaseExtractor

class AltExtractor(BaseExtractor):
    """
    Extracts alt-related information from images, pictures, and SVGs.
    Captures alt text, title, and src attributes.
    """

    def filter(self, el: Dict[str, Any]) -> bool:
        # Only apply to elements that normally have alternative text
        tag = el["tag"].lower()
        return tag in ("img", "picture", "svg")

    def extract(self, el: Dict[str, Any]) -> Dict[str, Any]:
        attrs = el.get("attributes", {})
        return {
            "alt_text": attrs.get("alt"),
            "title": attrs.get("title"),
            "src": attrs.get("src"),
        }
