import pytest
from app.services.analytics.rules_analyzer.rule_focus_visible import Rule247FocusVisible
from app.services.analytics.json_parser.models import (
    DocumentInfo,
    DocumentModel,
    ElementNode,
    NodeInteraction
)


class TestRule247FocusVisible:

    def test_no_violations_without_outline_none(self):
        button = ElementNode(
            tag="button",
            node_id="btn1",
            text="Submit",
            styles={"outline": "2px solid blue"},
            computed={}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[button]
        )
        rule = Rule247FocusVisible()
        violations = rule.check(doc_model)
        assert violations == []

    def test_no_violations_outline_none_on_non_interactive_element(self):
        div = ElementNode(
            tag="div",
            node_id="div1",
            text="Content",
            styles={"outline": "none"},
            computed={}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[div]
        )
        rule = Rule247FocusVisible()
        violations = rule.check(doc_model)
        assert violations == []

    def test_violations_outline_none_on_interactive_element(self):
        button = ElementNode(
            tag="button",
            node_id="btn2",
            text="Submit",
            styles={"outline": "none"},
            computed={}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[button]
        )
        rule = Rule247FocusVisible()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        assert violations[0].element_id == "btn2"
        assert "outline: none" in violations[0].message
        assert violations[0].rule_id == "2.4.7"

    def test_no_violations_outline_none_on_element_with_negative_tabindex(self):
        div_not_focusable = ElementNode(
            tag="div",
            node_id="div3",
            text="Not focusable",
            styles={"outline": "none"},
            computed={},
            attributes={"tabindex": "-1"}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[div_not_focusable]
        )
        rule = Rule247FocusVisible()
        violations = rule.check(doc_model)
        assert violations == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])