from typing import Dict, Any
from app.services.accessibility.base_extractor import BaseExtractor

class TextExtractor(BaseExtractor):
    def extract(self, el: Dict[str, Any]) -> Dict[str, Any]:
        text = (el.get("text") or "").strip()
        return {"text": text} if text else {}
