import pytest
from app.services.analytics.rules_analyzer.rule_label import Rule131Label
from app.services.analytics.json_parser.models import (
    DocumentInfo,
    DocumentModel,
    ElementNode,
    NodeSemantics
)

class TestRule131Label:

    def test_no_violations_with_placeholder(self):
        input_with_placeholder = ElementNode(
            tag="input",
            node_id="input1",
            placeholder="Enter name",
            attributes={"type": "text"}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[input_with_placeholder]
        )
        rule = Rule131Label()
        violations = rule.check(doc_model)
        assert violations == []

    def test_no_violations_with_aria_label(self):
        input_with_aria_label = ElementNode(
            tag="input",
            node_id="input2",
            attributes={"type": "text"},
            semantics=NodeSemantics(aria_label="Email Input")
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[input_with_aria_label]
        )
        rule = Rule131Label()
        violations = rule.check(doc_model)
        assert violations == []

    def test_no_violations_with_aria_labelledby(self):
        input_with_aria_labelledby = ElementNode(
            tag="input",
            node_id="input3",
            attributes={"type": "text"},
            semantics=NodeSemantics(aria_labelledby=["label1"])
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[input_with_aria_labelledby]
        )
        rule = Rule131Label()
        violations = rule.check(doc_model)
        assert violations == []

    def test_violations_with_no_label_equivalent(self):
        input_no_label = ElementNode(
            tag="input",
            node_id="input4",
            attributes={"type": "text"},
            semantics=NodeSemantics(aria_label=None)
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[input_no_label]
        )
        rule = Rule131Label()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        assert violations[0].element_id == "input4"
        assert "has no associated label" in violations[0].message
        assert violations[0].rule_id == "1.3.1"

    def test_mixed_form_elements(self):
        input_with_placeholder = ElementNode(
            tag="input",
            node_id="input1",
            placeholder="Name",
            attributes={"type": "text"}
        )
        textarea_with_aria_label = ElementNode(
            tag="textarea",
            node_id="textarea1",
            attributes={},
            semantics=NodeSemantics(aria_label="Description")
        )
        select_no_label = ElementNode(
            tag="select",
            node_id="select1",
            attributes={},
            semantics=NodeSemantics(aria_label=None)
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[input_with_placeholder, textarea_with_aria_label, select_no_label]
        )
        rule = Rule131Label()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        assert violations[0].element_id == "select1"
        assert violations[0].rule_id == "1.3.1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])