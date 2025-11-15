import pytest
from app.services.analytics.rules_analyzer.rule_alt_atribute import Rule111MissingAlt
from app.services.analytics.json_parser.models import (
    DocumentInfo,
    DocumentModel,
    ElementNode
)

class TestRule111MissingAlt:

    def test_no_violations_with_alt(self):
        img_with_alt = ElementNode(
            tag="img",
            node_id="img1",
            alt="A cat",
            attributes={"src": "cat.jpg"}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[img_with_alt]
        )
        rule = Rule111MissingAlt()
        violations = rule.check(doc_model)
        assert violations == []

    def test_violations_with_empty_alt(self):
        img_with_empty_alt = ElementNode(
            tag="img",
            node_id="img2",
            alt="",
            attributes={"src": "dog.jpg"}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[img_with_empty_alt]
        )
        rule = Rule111MissingAlt()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        assert violations[0].element_id == "img2"
        assert "has no 'alt' attribute or it is empty" in violations[0].message
        assert violations[0].rule_id == "1.1.1"

    def test_violations_with_none_alt(self):
        img_with_none_alt = ElementNode(
            tag="img",
            node_id="img3",
            alt=None,
            attributes={"src": "bird.jpg"}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[img_with_none_alt]
        )
        rule = Rule111MissingAlt()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        assert violations[0].element_id == "img3"
        assert "has no 'alt' attribute or it is empty" in violations[0].message
        assert violations[0].rule_id == "1.1.1"

    def test_mixed_images(self):
        img_with_alt = ElementNode(
            tag="img",
            node_id="img1",
            alt="A cat",
            attributes={"src": "cat.jpg"}
        )
        img_with_empty_alt = ElementNode(
            tag="img",
            node_id="img2",
            alt="",
            attributes={"src": "dog.jpg"}
        )
        img_with_none_alt = ElementNode(
            tag="img",
            node_id="img3",
            alt=None,
            attributes={"src": "bird.jpg"}
        )
        doc_model = DocumentModel(
            info=DocumentInfo(title="Test", lang="en"),
            root=ElementNode(tag="html"),
            elements=[img_with_alt, img_with_empty_alt, img_with_none_alt]
        )
        rule = Rule111MissingAlt()
        violations = rule.check(doc_model)
        assert len(violations) == 2
        violation_ids = {v.element_id for v in violations}
        assert violation_ids == {"img2", "img3"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])