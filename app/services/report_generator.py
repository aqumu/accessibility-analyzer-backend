from typing import Dict, Any

def generate_report(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combine analyzer outputs into a high-level summary report.
    """
    total_score = 0
    count = 0
    for res in analyzer_results.values():
        score = res.get("score")
        if score is not None:
            total_score += score
            count += 1

    avg_score = round(total_score / count, 2) if count else 0

    return {
        "overall_score": avg_score,
        "analyzer_details": analyzer_results,
        "summary": f"Average accessibility score: {avg_score}",
    }
