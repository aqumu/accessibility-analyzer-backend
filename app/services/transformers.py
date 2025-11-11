# app/services/transformers.py
from typing import Dict, Any, List
from app.schemas import RunResult, PageSummary, ElementData, ElementAttributes, ElementVisibility, ElementColors
from pydantic import HttpUrl

def transform_fetch_result(raw: Dict[str, Any]) -> RunResult:
    summary = PageSummary(
        total_elements=raw.get("summary", {}).get("total_elements", 0),
        interactive_elements=raw.get("summary", {}).get("interactive_elements", 0),
    )

    elements: List[ElementData] = []
    for el in raw.get("elements", []):
        css = el.get("css", {}) or {}
        attrs = el.get("attributes", {}) or {}
        aria = el.get("aria", {}) or {}

        element = ElementData(
            tag=el.get("tag", ""),
            id=el.get("id"),
            class_=el.get("class"),
            role=el.get("role"),
            aria={k: v for k, v in (aria.items() if isinstance(aria, dict) else [])},
            attributes=ElementAttributes(
                alt=attrs.get("alt"),
                title=attrs.get("title"),
                tabindex=attrs.get("tabindex"),
            ),
            visibility=ElementVisibility(
                display=css.get("display"),
                visibility=css.get("visibility"),
            ),
            colors=ElementColors(
                text=css.get("color"),
                background=css.get("backgroundColor"),
            ),
            text=el.get("text"),
        )
        elements.append(element)

    return RunResult(summary=summary, elements=elements)
