import pytest
from app.services.analytics.rules_analyzer.rule_3_1_1_language import Rule311Language
from app.services.analytics.json_parser.models import (
    DocumentInfo,
    DocumentModel,
    ElementNode
)

class TestRule311Language:
    def test_no_violations_with_lang(self):
        doc_info = DocumentInfo(url="https://example.com", title="Test", lang="en-US")
        doc_model = DocumentModel(
            info=doc_info,
            root=ElementNode(tag="html"),
            elements=[]
        )
        rule = Rule311Language()
        violations = rule.check(doc_model)
        assert violations == []

    def test_violations_with_no_lang(self):
        doc_info = DocumentInfo(url="https://example.com", title="Test", lang=None)
        doc_model = DocumentModel(
            info=doc_info,
            root=ElementNode(tag="html"),
            elements=[]
        )
        rule = Rule311Language()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        assert violations[0].element_id == "document"
        assert "does not have a language specification" in violations[0].message
        assert violations[0].rule_id == "3.1.1"

    def test_violations_with_empty_lang(self):
        doc_info = DocumentInfo(url="https://example.com", title="Test", lang="")
        doc_model = DocumentModel(
            info=doc_info,
            root=ElementNode(tag="html"),
            elements=[]
        )
        rule = Rule311Language()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        assert violations[0].element_id == "document"
        assert "does not have a language specification" in violations[0].message
        assert violations[0].rule_id == "3.1.1"

    def test_violations_with_whitespace_lang(self):
        doc_info = DocumentInfo(url="https://example.com", title="Test", lang="   ")
        doc_model = DocumentModel(
            info=doc_info,
            root=ElementNode(tag="html"),
            elements=[]
        )
        rule = Rule311Language()
        violations = rule.check(doc_model)
        assert len(violations) == 1
        assert violations[0].element_id == "document"
        assert "does not have a language specification" in violations[0].message
        assert violations[0].rule_id == "3.1.1"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])