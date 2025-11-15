from typing import List

from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation


class RulePlaceholderWithoutLabel(WCAGRule):
    id = "form-placeholder-no-label"
    description = "Поле формы не должно использовать только placeholder вместо label"

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        from app.services.analytics.data_group.data_group import DataGroupExtractor
        fields = DataGroupExtractor.extract_form_field_data(document)

        violations = []
        for f in fields:
            has_label = f.has_explicit_label or f.aria_label or f.aria_labelledby
            if not has_label and f.placeholder:
                violations.append(RuleViolation(
                    rule_id=self.id,
                    element_id=f.node_id,
                    message="Поле использует только placeholder и не имеет label."
                ))
        return violations
