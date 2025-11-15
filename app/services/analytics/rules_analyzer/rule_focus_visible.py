from typing import List
from app.services.analytics.data_group.data_group import DataGroupExtractor
from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation


class Rule247FocusVisible(WCAGRule):
    id = "2.4.7"
    description = "Elements must have a visible focus indicator."

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        violations = []

        style_data_list = DataGroupExtractor.extract_style_data(document)

        interactive_data_list = DataGroupExtractor.extract_interactive_data(document)
        interactive_ids = {elem.node_id for elem in interactive_data_list}

        for style_data in style_data_list:
            outline_none_in_styles = style_data.styles.get('outline') == 'none'
            outline_none_in_computed = style_data.computed.get('outline') == 'none'

            if outline_none_in_styles or outline_none_in_computed:
                potentially_focusable_tags = {
                    'a', 'button', 'input', 'textarea', 'select', 'area', 'summary',
                    'audio', 'video', 'iframe', 'object', 'embed'
                }
                is_interactive = style_data.node_id in interactive_ids
                is_default_focusable = style_data.tag in potentially_focusable_tags

                has_explicit_negative_tabindex = False
                for d in interactive_data_list:
                    if d.node_id == style_data.node_id and d.tabindex == -1:
                        has_explicit_negative_tabindex = True
                        break

                if (is_interactive or is_default_focusable) and not has_explicit_negative_tabindex:
                    violation = RuleViolation(
                        rule_id=self.id,
                        element_id=style_data.node_id,
                        message=f"Element (tag: {style_data.tag}) has 'outline: none' which may remove the visible focus indicator."
                    )
                    violations.append(violation)

        return violations