from typing import List

from app.services.analytics.data_group.data_group import DataGroupExtractor
from app.services.analytics.json_parser.models import DocumentModel
from app.services.analytics.rules_analyzer.analyzer import WCAGRule, RuleViolation


class Rule122CaptionsMedia(WCAGRule):
    id = "1.2.2"
    description = "Synchronized media (video/audio) must have captions or a transcript."

    def check(self, document: DocumentModel) -> List[RuleViolation]:
        violations = []

        media_data_list = DataGroupExtractor.extract_media_data(document)

        for media_data in media_data_list:
            if media_data.tag in ['video', 'audio']:
                source_element = next((elem for elem in document.elements if elem.node_id == media_data.node_id), None)

                if source_element:
                    has_track = False
                    for child in source_element.children:
                        if child.tag == 'track' and child.attributes.get('kind') in ['captions', 'subtitles']:
                            has_track = True
                            break

                    if not has_track:
                        has_transcript_nearby = False
                        for elem in document.elements:
                            if elem.node_id != media_data.node_id:  # Не сам элемент
                                if any('transcript' in cls.lower() for cls in elem.classes):
                                    if elem.text and len(
                                            elem.text.strip()) > 10:
                                        has_transcript_nearby = True
                                        break

                        if not has_transcript_nearby:
                            violation = RuleViolation(
                                rule_id=self.id,
                                element_id=media_data.node_id,
                                message=f"Media element (tag: {media_data.tag}, ID: {media_data.node_id}) does not have associated captions (track) or a transcript nearby."
                            )
                            violations.append(violation)

        return violations
