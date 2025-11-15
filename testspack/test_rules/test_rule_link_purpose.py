import pytest
from app.services.analytics.rules_analyzer.rule_link_button_purpose import Rule412LinkPurpose
from app.services.analytics.json_parser.models import (
    DocumentInfo,
    DocumentModel,
    ElementNode,
    NodeSemantics
)

class TestRule412LinkPurpose:

    def test_no_violations_with_text(self):
        link_with_text = ElementNode(
            tag="a",
            node_id="link1",
            text="Click here",
            attributes={"href": "/page"}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[link_with_text]
        )
        rule = Rule412LinkPurpose()
        violations = rule.check(doc_model)
        assert violations == []

    def test_no_violations_with_aria_label(self):
        link_with_aria_label = ElementNode(
            tag="a",
            node_id="link2",
            text="",
            attributes={"href": "/page"},
            semantics=NodeSemantics(aria_label="Go to page")
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[link_with_aria_label]
        )
        rule = Rule412LinkPurpose()
        violations = rule.check(doc_model)
        assert violations == []

    def test_violations_with_no_text_or_aria_label(self):
        link_no_text = ElementNode(
            tag="a",
            node_id="link3",
            text="",
            attributes={"href": "/page"},
            semantics=NodeSemantics(aria_label=None)
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[link_no_text]
        )
        rule = Rule412LinkPurpose()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        assert violations[0].element_id == "link3"
        assert "has no discernible text or aria-label" in violations[0].message
        assert violations[0].rule_id == "4.1.2"

    def test_button_with_text(self):
        button_with_text = ElementNode(
            tag="button",
            node_id="btn1",
            text="Submit",
            attributes={}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[button_with_text]
        )
        rule = Rule412LinkPurpose()
        violations = rule.check(doc_model)
        assert violations == []

    def test_button_with_aria_label(self):
        button_with_aria_label = ElementNode(
            tag="button",
            node_id="btn2",
            text="",
            attributes={},
            semantics=NodeSemantics(aria_label="Submit form")
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[button_with_aria_label]
        )
        rule = Rule412LinkPurpose()
        violations = rule.check(doc_model)
        assert violations == []

    def test_button_no_text_or_aria_label(self):
        button_no_text = ElementNode(
            tag="button",
            node_id="btn3",
            text="",
            attributes={},
            semantics=NodeSemantics(aria_label=None)
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[button_no_text]
        )
        rule = Rule412LinkPurpose()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        assert violations[0].element_id == "btn3"
        assert "has no discernible text or aria-label" in violations[0].message
        assert violations[0].rule_id == "4.1.2"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])