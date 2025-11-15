from typing import List

from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation


class RuleMediaAutoplay(WCAGRule):
    id = "media-autoplay-audio"
    description = "Видео не должно автоматически воспроизводиться со звуком"

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        from app.services.analytics.data_group.data_group import DataGroupExtractor
        media_items = DataGroupExtractor.extract_media_data(document)

        violations = []
        for m in media_items:
            if m.tag == "video" and m.autoplay is not None and not m.muted:
                violations.append(RuleViolation(
                    rule_id=self.id,
                    element_id=m.node_id,
                    message="Видео запускается автоматически с включённым звуком."
                ))
        return violations
