from typing import List

from app.services.analytics.data_group.data_group import DataGroupExtractor
from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation


class Rule243FocusOrder(WCAGRule):
    id = "2.4.3"
    description = "Elements should not use tabindex > 0 or tabindex = -1."

    def check(self, document: DocumentModel) -> List[RuleViolation]:

        violations = []

        interactive_data_list = DataGroupExtractor.extract_interactive_data(document)

        for element_data in interactive_data_list:
            tabindex = element_data.tabindex

            if tabindex is not None:
                try:
                    tabindex_val = int(tabindex)
                    if tabindex_val > 0 or tabindex_val == -1:
                        violation = RuleViolation(
                            rule_id=self.id,
                            element_id=element_data.node_id,
                            message=f"Element (tag: {element_data.tag}) has invalid tabindex '{tabindex_val}'."
                        )
                        violations.append(violation)
                except ValueError:
                    violation = RuleViolation(
                        rule_id=self.id,
                        element_id=element_data.node_id,
                        message=f"Element (tag: {element_data.tag}) has non-numeric tabindex '{tabindex}'."
                    )
                    violations.append(violation)

        return violations