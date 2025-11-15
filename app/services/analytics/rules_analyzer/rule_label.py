from typing import List
from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation
from app.services.analytics.data_group.data_group import DataGroupExtractor

class Rule131Label(WCAGRule):
    id = "1.3.1"
    description = "Form elements must have a label or an equivalent (aria-label, placeholder)."

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        violations = []
        form_data_list = DataGroupExtractor.extract_form_field_data(document)

        for field_data in form_data_list:
            has_aria_label = bool(field_data.aria_label)
            has_aria_labelledby = bool(field_data.aria_labelledby)
            has_placeholder = bool(field_data.placeholder)

            if not has_aria_label and not has_aria_labelledby and not has_placeholder:
                violation = RuleViolation(
                    rule_id=self.id,
                    element_id=field_data.node_id,
                    message=f"Form element (tag: {field_data.tag}) has no associated label (aria-label, aria-labelledby, or placeholder)."
                )
                violations.append(violation)
        return violations