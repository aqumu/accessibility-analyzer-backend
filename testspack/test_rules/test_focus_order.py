import pytest

from app.services.analytics.json_parser.models import DocumentModel, DocumentInfo, ElementNode, NodeInteraction
from app.services.analytics.rules_analyzer.rule_focus_order import Rule243FocusOrder


class TestRule243FocusOrder:

    def test_no_violations_with_valid_tabindex(self):
        button_valid = ElementNode(
            tag="button",
            node_id="btn1",
            text="Submit",
            attributes={},
            interaction=NodeInteraction(tabindex=0)
        )
        link_no_tabindex = ElementNode(
            tag="a",
            node_id="link1",
            text="Go",
            attributes={"href": "/page"}
        )
        input_valid_attr = ElementNode(
            tag="input",
            node_id="input1",
            attributes={"tabindex": "0", "type": "text"}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[button_valid, link_no_tabindex, input_valid_attr]
        )
        rule = Rule243FocusOrder()
        violations = rule.check(doc_model)
        assert violations == []

    def test_violations_with_tabindex_gt_zero(self):
        button_invalid = ElementNode(
            tag="button",
            node_id="btn2",
            text="Submit",
            attributes={},
            interaction=NodeInteraction(tabindex=2)
        )
        input_invalid_attr = ElementNode(
            tag="input",
            node_id="input2",
            attributes={"tabindex": "5", "type": "text"}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[button_invalid, input_invalid_attr]
        )
        rule = Rule243FocusOrder()
        violations = rule.check(doc_model)
        assert len(violations) == 2
        violation_ids = {v.element_id for v in violations}
        assert violation_ids == {"btn2", "input2"}
        for v in violations:
            assert "has invalid tabindex" in v.message
            assert v.rule_id == "2.4.3"
        tabindex_values = {v.message.split("'")[1] for v in violations}
        assert "2" in tabindex_values
        assert "5" in tabindex_values

    def test_violations_with_tabindex_minus_one(self):
        button_invalid = ElementNode(
            tag="button",
            node_id="btn3",
            text="Submit",
            attributes={},
            interaction=NodeInteraction(tabindex=-1)
        )
        link_invalid_attr = ElementNode(
            tag="a",
            node_id="link2",
            text="Go",
            attributes={"href": "/page", "tabindex": "-1"}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[button_invalid, link_invalid_attr]
        )
        rule = Rule243FocusOrder()
        violations = rule.check(doc_model)
        assert len(violations) == 2
        violation_ids = {v.element_id for v in violations}
        assert violation_ids == {"btn3", "link2"}
        for v in violations:
            assert "has invalid tabindex" in v.message
            assert v.rule_id == "2.4.3"
        tabindex_values = {v.message.split("'")[1] for v in violations}
        assert "-1" in tabindex_values

    def test_violations_with_non_numeric_tabindex(self):
        input_invalid_attr = ElementNode(
            tag="input",
            node_id="input3",
            attributes={"tabindex": "not_a_number", "type": "text"}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[input_invalid_attr]
        )
        rule = Rule243FocusOrder()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        violation_ids = {v.element_id for v in violations}
        assert violation_ids == {"input3"}
        for v in violations:
            assert "non-numeric tabindex" in v.message
            assert v.rule_id == "2.4.3"
        tabindex_values = {v.message.split("'")[1] for v in violations}
        assert "not_a_number" in tabindex_values


    def test_no_interactive_elements(self):
        div1 = ElementNode(
            tag="div",
            node_id="div1",
            text="Content"
        )
        span1 = ElementNode(
            tag="span",
            node_id="span1",
            text="More content"
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[div1, span1]
        )
        rule = Rule243FocusOrder()
        violations = rule.check(doc_model)
        assert violations == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])