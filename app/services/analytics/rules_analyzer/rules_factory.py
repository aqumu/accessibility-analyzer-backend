# app/services/analytics/rules_analyzer/rules_factory.py

from typing import List, Dict, Any, Tuple

from app.services.analytics.data_group.data_group import (
    DataGroupExtractor,
    ImageData,
    FormFieldData,
    MediaData,
    TableData,
    InteractiveData,
    AriaData,
    StyleData,
    HeadingData,
    DocumentStructureData,
)

# WCAG rules:
from app.services.analytics.rules_analyzer.rule_auto_start_sound import RuleMediaAutoplay
from app.services.analytics.rules_analyzer.rule_3_1_1_language import Rule311Language
from app.services.analytics.rules_analyzer.rule_contrast import Rule143ContrastMinimum
from app.services.analytics.rules_analyzer.rule_empty_link import Rule244LinkPurpose
from app.services.analytics.rules_analyzer.rule_focus_order import Rule243FocusOrder
from app.services.analytics.rules_analyzer.rule_focus_visible import Rule247FocusVisible
from app.services.analytics.rules_analyzer.rule_heading_structure import Rule131HeadingsStructure
from app.services.analytics.rules_analyzer.rule_media import Rule122CaptionsMedia
from app.services.analytics.rules_analyzer.rule_paceholder import RulePlaceholderWithoutLabel
from app.services.analytics.rules_analyzer.rule_tables_sh import RuleTableNoHeaders
from app.services.analytics.rules_analyzer.rule_title import Rule412IFrameTitle
from app.services.analytics.rules_analyzer.rules_aria_label import RuleAriaIncorrectUsage
from app.services.analytics.rules_analyzer.rule_label import Rule131Label
from app.services.analytics.rules_analyzer.rule_alt_atribute import Rule111MissingAlt
from app.services.analytics.rules_analyzer.rule_link_button_purpose import Rule412LinkPurpose


class RulesFactory:
    """
    Фабрика, которая:
    - получает DocumentModel
    - вызывает DataGroupExtractor
    - создаёт правила LAZY
    - сопоставляет правила с полученными дата-группами
    """

    def __init__(self, extractor: DataGroupExtractor | None = None):
        self.extractor = extractor or DataGroupExtractor()

        # Маппинг "тип данных → список классов правил"
        self.RULES_MAP = {
            ImageData: [Rule111MissingAlt],
            MediaData: [RuleMediaAutoplay, Rule122CaptionsMedia, Rule412IFrameTitle],
            FormFieldData: [RulePlaceholderWithoutLabel, Rule131Label],
            TableData: [RuleTableNoHeaders],
            InteractiveData: [Rule412LinkPurpose, Rule244LinkPurpose, Rule243FocusOrder],
            HeadingData: [Rule131HeadingsStructure],
            StyleData: [Rule143ContrastMinimum, Rule247FocusVisible],
            AriaData: [RuleAriaIncorrectUsage],
            DocumentStructureData: [Rule311Language],
        }

    def get_rules(self, document_model) -> List[Tuple[Any, List[Any]]]:
        """Возвращает список кортежей:
        (экземпляр правила, список связанных DataGroup объектов)
        """

        # 1. Собираем все дата-группы
        groups: Dict[type, List[Any]] = {
            ImageData: self.extractor.extract_image_data(document_model),
            MediaData: self.extractor.extract_media_data(document_model),
            FormFieldData: self.extractor.extract_form_field_data(document_model),
            TableData: self.extractor.extract_table_data(document_model),
            InteractiveData: self.extractor.extract_interactive_data(document_model),
            HeadingData: self.extractor.extract_heading_data(document_model),
            StyleData: self.extractor.extract_style_data(document_model),
            AriaData: self.extractor.extract_aria_data(document_model),
            DocumentStructureData: [self.extractor.extract_document_structure_data(document_model)],
        }

        result: List[Tuple[Any, List[Any]]] = []

        # 2. Для каждой дата-группы — подключаем правила
        for group_type, items in groups.items():
            if not items:
                continue  # пропуск пустых групп

            rule_classes = self.RULES_MAP.get(group_type, [])
            for rule_class in rule_classes:
                rule_instance = rule_class()  # lazy creation
                result.append((rule_instance, items))

        return result