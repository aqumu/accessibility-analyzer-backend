from typing import Dict, Any
from app.services.accessibility.base_extractor import BaseExtractor

class VisibilityExtractor(BaseExtractor):
    def extract(self, el: Dict[str, Any]) -> Dict[str, Any]:
        css = el.get("css", {})
        return {
            "is_hidden": (
                css.get("display") == "none" or
                css.get("visibility") == "hidden" or
                css.get("opacity") == "0"
            )
        }
