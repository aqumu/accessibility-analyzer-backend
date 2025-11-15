import pytest
from app.services.analytics.rules_analyzer.rule_contrast import Rule143ContrastMinimum
from app.services.analytics.json_parser.models import (
    DocumentInfo,
    DocumentModel,
    ElementNode,
)


class TestRule143ContrastMinimum:

    def test_no_violations_good_contrast(self):
        div_good = ElementNode(
            tag="div",
            node_id="div_good",
            text="Good contrast text",
            color="rgb(0, 0, 0)", # Black
            backgroundColor="rgb(255, 255, 255)", # White
            styles={"color": "rgb(0, 0, 0)", "backgroundColor": "rgb(255, 255, 255)"},
            computed={}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[div_good]
        )
        rule = Rule143ContrastMinimum()
        violations = rule.check(doc_model)
        assert violations == []

    def test_violations_bad_contrast(self):
        div_bad = ElementNode(
            tag="div",
            node_id="div_bad",
            text="Low contrast text",
            color="rgb(220, 220, 220)", # Light grey
            backgroundColor="rgb(240, 240, 240)", # Very light grey
            styles={"color": "rgb(200, 200, 200)", "backgroundColor": "rgb(240, 240, 240)"},
            computed={}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[div_bad]
        )
        rule = Rule143ContrastMinimum()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        assert violations[0].element_id == "div_bad"
        assert "insufficient contrast" in violations[0].message
        assert violations[0].rule_id == "1.4.3"
        assert "1.21:1" in violations[0].message or "1.20:1" in violations[0].message

    def test_no_violations_missing_color_or_bg(self):
        div_no_color = ElementNode(
            tag="div",
            node_id="div_no_color",
            text="No color specified",
            color=None,
            backgroundColor="rgb(255, 255, 255)",
            styles={"backgroundColor": "rgb(255, 255, 255)"},
            computed={}
        )
        div_no_bg = ElementNode(
            tag="div",
            node_id="div_no_bg",
            text="No bg specified",
            color="rgb(0, 0, 0)",
            backgroundColor=None,
            styles={"color": "rgb(0, 0, 0)"},
            computed={}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[div_no_color, div_no_bg]
        )
        rule = Rule143ContrastMinimum()
        violations = rule.check(doc_model)
        assert violations == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])