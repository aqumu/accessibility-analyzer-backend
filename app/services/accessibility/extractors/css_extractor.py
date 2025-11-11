from typing import Dict, Any
from app.services.accessibility.base_extractor import BaseExtractor

class CssExtractor(BaseExtractor):
    def extract(self, el: Dict[str, Any]) -> Dict[str, Any]:
        css = el.get("css", {})
        if not css:
            return {}
        return {
            "colors": {
                "text": css.get("color"),
                "background": css.get("backgroundColor"),
            },
            "font": {
                "family": css.get("fontFamily"),
                "size": css.get("fontSize"),
                "weight": css.get("fontWeight"),
                "line_height": css.get("lineHeight"),
                "letter_spacing": css.get("letterSpacing"),
            },
            "layout": {
                "display": css.get("display"),
                "visibility": css.get("visibility"),
                "position": css.get("position"),
                "width": css.get("width"),
                "height": css.get("height"),
            },
        }
