from typing import Dict, Any
from app.services.accessibility.base_extractor import BaseExtractor

class LinkExtractor(BaseExtractor):
    """
    Extracts accessibility-relevant info from links (<a> elements).
    Captures href, target, rel, and visible text.
    """

    def filter(self, el: Dict[str, Any]) -> bool:
        return el["tag"].lower() == "a"

    def extract(self, el: Dict[str, Any]) -> Dict[str, Any]:
        attrs = el.get("attributes", {})
        return {
            "href": attrs.get("href"),
            "target": attrs.get("target"),
            "rel": attrs.get("rel"),
            "text": (el.get("text") or "").strip()
        }
