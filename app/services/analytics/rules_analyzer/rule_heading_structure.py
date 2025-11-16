from typing import List

from app.services.analytics.data_group.data_group import DataGroupExtractor
from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation


class Rule131HeadingsStructure(WCAGRule):
    id = "1.3.1"
    description = "Headings should be structured correctly (one H1, proper hierarchy)."

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        violations = []

        heading_data_list = DataGroupExtractor.extract_heading_data(document)

        h1_count = 0
        h1_ids = []
        for hd in heading_data_list:
            if hd.tag.lower() == 'h1':
                h1_count += 1
                h1_ids.append(hd.node_id)

        if h1_count > 1:
            violation = RuleViolation(
                rule_id=self.id,
                element_id=h1_ids[0],
                message=f"Document has {h1_count} H1 elements (IDs: {h1_ids}). Only one H1 is recommended per page."
            )
            violations.append(violation)

        last_level = 0
        for hd in heading_data_list:
            tag = hd.tag.lower()
            current_level = int(tag[1])  # h1 -> 1, h2 -> 2, ...

            if current_level > last_level + 1:
                violation = RuleViolation(
                    rule_id=self.id,
                    element_id=hd.node_id,
                    message=f"Heading element (tag: {hd.tag}, ID: {hd.node_id}) violates hierarchy. Previous level was H{last_level}, current is H{current_level}."
                )
                violations.append(violation)

            last_level = current_level

        return violations
