from typing import Dict, Any
from app.services.accessibility.base_extractor import BaseExtractor

# Semantic and landmark elements
SEMANTIC_TAGS = {
    "header", "footer", "main", "nav", "aside", "section", "article", "form", "fieldset",
    "h1", "h2", "h3", "h4", "h5", "h6"
}

class SemanticExtractor(BaseExtractor):
    """
    Extracts semantic/landmark elements including headings.
    Captures tag, id, class, role, and text content.
    """

    def filter(self, el: Dict[str, Any]) -> bool:
        return el["tag"].lower() in SEMANTIC_TAGS

    def extract(self, el: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "tag": el["tag"].lower(),
            "id": el.get("id"),
            "class": el.get("class"),
            "role": el.get("role"),
            "text": (el.get("text") or "").strip()
        }
