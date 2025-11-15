from typing import List

from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation

class RuleTableNoHeaders(WCAGRule):
    id = "table-no-headers"
    description = "Таблица должна содержать хотя бы один <th>"

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        from app.services.analytics.data_group.data_group import DataGroupExtractor
        tables = DataGroupExtractor.extract_table_data(document)

        violations = []
        for t in tables:
            if t.tag == "table":
                has_th = any(child.tag == "th" for child in t.children)
                if not has_th:
                    violations.append(RuleViolation(
                        rule_id=self.id,
                        element_id=t.node_id,
                        message="Таблица не содержит заголовков (<th>)."
                    ))
        return violations
