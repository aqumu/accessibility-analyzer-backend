from typing import List

from app.services.analytics.data_group.data_group import DataGroupExtractor
from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation


class Rule143ContrastMinimum(WCAGRule):
    id = "1.4.3"
    description = "Text and background colors must have sufficient contrast (4.5:1 for normal text)."

    def _parse_color(self, color_str: str) -> tuple[float, float, float]:
        if not color_str:
            return (0.0, 0.0, 0.0)

        if color_str.startswith('rgb(') or color_str.startswith('rgba('):
            import re
            nums = re.findall(r'\d+', color_str)
            r, g, b = int(nums[0]), int(nums[1]), int(nums[2])
            return (r / 255.0, g / 255.0, b / 255.0)
        elif color_str.startswith('#'):
            hex_color = color_str[1:]
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return (r, g, b)
        else:
            return (0.0, 0.0, 0.0)

    def _relative_luminance(self, r: float, g: float, b: float) -> float:
        def lum(c):
            if c <= 0.03928:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4

        r_srgb = lum(r)
        g_srgb = lum(g)
        b_srgb = lum(b)

        return 0.2126 * r_srgb + 0.7152 * g_srgb + 0.0722 * b_srgb

    def _contrast_ratio(self, color1: str, color2: str) -> float:
        r1, g1, b1 = self._parse_color(color1)
        r2, g2, b2 = self._parse_color(color2)

        lum1 = self._relative_luminance(r1, g1, b1)
        lum2 = self._relative_luminance(r2, g2, b2)

        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)

        return (lighter + 0.05) / (darker + 0.05)

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        violations = []

        style_data_list = DataGroupExtractor.extract_style_data(document)

        for style_data in style_data_list:
            text_color = style_data.color
            bg_color = style_data.backgroundColor

            if text_color and bg_color:
                contrast = self._contrast_ratio(text_color, bg_color)

                if contrast < 4.5:
                    violation = RuleViolation(
                        rule_id=self.id,
                        element_id=style_data.node_id,
                        message=f"Element (tag: {style_data.tag}) has insufficient contrast ({contrast:.2f}:1) between text color '{text_color}' and background color '{bg_color}'."
                    )
                    violations.append(violation)

        return violations
