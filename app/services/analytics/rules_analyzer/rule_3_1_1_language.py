from typing import List
from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation

class Rule311Language(WCAGRule):
    id = "3.1.1"
    description = "Pages need language specification"

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        violations = []
        if document.info.lang is None or document.info.lang.strip() == "":
            violation = RuleViolation(
                rule_id=self.id,
                element_id="document",
                message="Document does not have a language specification (lang attribute on <html>)."
            )
            violations.append(violation)
        return violations