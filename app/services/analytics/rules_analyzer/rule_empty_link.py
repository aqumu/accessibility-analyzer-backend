from typing import List
from app.services.analytics.data_group.data_group import DataGroupExtractor
from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation


class Rule244LinkPurpose(WCAGRule):
    id = "2.4.4"
    description = "Links must have a discernible purpose."

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        violations = []

        interactive_data_list = DataGroupExtractor.extract_interactive_data(document)

        for element_data in interactive_data_list:
            if element_data.tag == 'a':
                has_discernible_text = bool(element_data.text and element_data.text.strip())
                has_aria_label = bool(element_data.aria_label)

                href = element_data.attributes.get('href', '')

                if href == '#' and not has_discernible_text and not has_aria_label:
                    violation = RuleViolation(
                        rule_id=self.id,
                        element_id=element_data.node_id,
                        message=f"Link element (href: '#') has no discernible text or aria-label."
                    )
                    violations.append(violation)

        return violations
