from typing import List
from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation


class Rule412IFrameTitle(WCAGRule):
    id = "4.1.2"
    description = "iframe elements must have a title attribute."

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        violations = []

        for element in document.elements:
            if element.tag.lower() == 'iframe':
                has_title_field = element.title is not None and element.title.strip() != ""
                has_title_attr = element.attributes.get('title') is not None and element.attributes.get('title').strip() != ""

                if not has_title_field and not has_title_attr:
                    violation = RuleViolation(
                        rule_id=self.id,
                        element_id=element.node_id,
                        message=f"iframe element (ID: {element.node_id}) does not have a 'title' attribute."
                    )
                    violations.append(violation)
        return violations
