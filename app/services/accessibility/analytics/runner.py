from typing import Dict, Any
from . import ANALYZERS

def run_analyzers(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes extractor results and runs each analyzer on its matching extractor output.
    Example input:
      { "AltExtractor": [ {...}, {...} ], "RoleExtractor": [ {...} ], ... }
    """
    results = {}
    for analyzer in ANALYZERS:
        # map analyzer name to corresponding extractor
        key = analyzer.name.replace("Analyzer", "Extractor")
        elements = extracted_data.get(key, [])
        result = analyzer.analyze(elements)
        results[analyzer.name] = result
    return results
