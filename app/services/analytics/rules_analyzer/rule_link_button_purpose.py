from typing import List
from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation
from app.services.analytics.data_group.data_group import DataGroupExtractor

class Rule412LinkPurpose(WCAGRule):
    id = "4.1.2"
    description = "Buttons and links must have discernible text or an aria-label."

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        violations = []

        interactive_data_list = DataGroupExtractor.extract_interactive_data(document)

        for element_data in interactive_data_list:
            has_discernible_text = bool(element_data.text and element_data.text.strip())
            has_aria_label = bool(element_data.aria_label)

            if not has_discernible_text and not has_aria_label:
                violation = RuleViolation(
                    rule_id=self.id,
                    element_id=element_data.node_id,
                    message=f"Interactive element (tag: {element_data.tag}) has no discernible text or aria-label."
                )
                violations.append(violation)
        return violations