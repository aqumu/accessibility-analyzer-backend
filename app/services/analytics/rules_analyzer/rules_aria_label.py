from typing import List

from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation


class RuleAriaIncorrectUsage(WCAGRule):
    id = "aria-incorrect"
    description = "Некорректное использование aria-атрибутов"

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        from app.services.analytics.data_group.data_group import DataGroupExtractor
        aria_items = DataGroupExtractor.extract_aria_data(document)

        violations = []
        for a in aria_items:
            is_hidden_style = False

            style = (a.semantics.computed if a.semantics else None)
            if style:
                if (
                    style.get("display") == "none" or
                    style.get("visibility") == "hidden"
                ):
                    is_hidden_style = True

            hidden_attr = a.attributes.get("hidden")

            # Ошибка: элемент скрыт, но aria-hidden запрещает скрытие
            if (is_hidden_style or hidden_attr is not None) and a.aria_hidden == False:
                violations.append(RuleViolation(
                    rule_id=self.id,
                    element_id=a.node_id,
                    message="Элемент скрыт, но aria-hidden='false', что нарушает доступность."
                ))

        return violations
