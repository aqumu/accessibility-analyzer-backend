from typing import Dict, Any, List

# import your extractors
from app.services.accessibility.extractors.aria_extractor import AriaExtractor
from app.services.accessibility.extractors.alt_extractor import AltExtractor
from app.services.accessibility.extractors.role_extractor import RoleExtractor
from app.services.accessibility.extractors.css_extractor import CssExtractor
from app.services.accessibility.extractors.text_extractor import TextExtractor
from app.services.accessibility.extractors.visibility_extractor import VisibilityExtractor
from app.services.accessibility.extractors.link_extractor import LinkExtractor
from app.services.accessibility.extractors.semantic_extractor import SemanticExtractor

EXTRACTORS = [
    AriaExtractor(),
    AltExtractor(),
    RoleExtractor(),
    CssExtractor(),
    TextExtractor(),
    VisibilityExtractor(),
    LinkExtractor(),
    SemanticExtractor(),
]

def run_extractors(raw_elements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Apply all extractors to all elements.
    Returns a dictionary keyed by extractor name with lists of extracted info.
    """
    results: Dict[str, List[Dict[str, Any]]] = {extractor.__class__.__name__: [] for extractor in EXTRACTORS}

    for el in raw_elements:
        for extractor in EXTRACTORS:
            if extractor.filter(el):
                extracted = extractor.extract(el)
                if extracted:  # skip empty dicts
                    results[extractor.__class__.__name__].append(extracted)

    return results
