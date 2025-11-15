from typing import List
from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation
from app.services.analytics.data_group.data_group import DataGroupExtractor

class Rule111MissingAlt(WCAGRule):
    id = "1.1.1"
    description = "All images must have an 'alt' attribute."

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        violations = []
        image_data_list = DataGroupExtractor.extract_image_data(document)

        for img_data in image_data_list:
            if not img_data.alt or img_data.alt.strip() == "":
                violation = RuleViolation(
                    rule_id=self.id,
                    element_id=img_data.node_id,
                    message=f"Image element (tag: {img_data.tag}) has no 'alt' attribute or it is empty."
                )
                violations.append(violation)
        return violations