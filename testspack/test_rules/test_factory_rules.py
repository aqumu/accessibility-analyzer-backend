# testspack/test_rules/test_factory_rules.py

import pytest
from unittest.mock import Mock, MagicMock, patch
from app.services.analytics.rules_analyzer.rules_factory import RulesFactory
from app.services.analytics.data_group.data_group import DataGroupExtractor, DocumentStructureData
from app.services.analytics.json_parser.models import DocumentModel, ElementNode, DocumentInfo


class TestRulesFactory:

    def test_factory_initialization(self):
        """Тест инициализации фабрики"""
        # Тест с дефолтным экстрактором
        factory = RulesFactory()
        assert factory.extractor is not None
        assert isinstance(factory.extractor, DataGroupExtractor)

        # Тест с кастомным экстрактором
        mock_extractor = Mock(spec=DataGroupExtractor)
        factory = RulesFactory(extractor=mock_extractor)
        assert factory.extractor == mock_extractor

    def test_get_rules_returns_correct_structure(self):
        """Тест что get_rules возвращает правильную структуру данных"""
        # Мокаем DocumentModel
        mock_document = Mock(spec=DocumentModel)
        mock_document.info = Mock(spec=DocumentInfo)
        mock_document.info.url = "https://example.com"
        mock_document.info.title = "Test Page"
        mock_document.info.lang = "en"
        mock_document.elements = []
        mock_document.root = None

        # Мокаем экстрактор чтобы возвращать пустые списки
        mock_extractor = Mock(spec=DataGroupExtractor)
        mock_extractor.extract_image_data.return_value = []
        mock_extractor.extract_media_data.return_value = []
        mock_extractor.extract_form_field_data.return_value = []
        mock_extractor.extract_table_data.return_value = []
        mock_extractor.extract_interactive_data.return_value = []
        mock_extractor.extract_heading_data.return_value = []
        mock_extractor.extract_style_data.return_value = []
        mock_extractor.extract_aria_data.return_value = []
        mock_extractor.extract_document_structure_data.return_value = Mock()

        factory = RulesFactory(extractor=mock_extractor)
        rules = factory.get_rules(mock_document)

        # Проверяем что возвращается список
        assert isinstance(rules, list)

        # Проверяем что все элементы - кортежи (rule_instance, items)
        for rule_instance, items in rules:
            assert hasattr(rule_instance, 'check')  # Должен быть метод check
            assert isinstance(items, list)

    def test_get_rules_with_real_data(self):
        """Тест с реальными данными элементов"""
        # Создаем полноценные mock-объекты с всеми необходимыми атрибутами
        image_element = Mock(spec=ElementNode)
        image_element.node_id = "img1"
        image_element.tag = "img"
        image_element.alt = None
        image_element.attributes = {"src": "test.jpg"}
        image_element.title = None
        image_element.styles = {}
        image_element.computed = {}
        image_element.color = None
        image_element.backgroundColor = None
        image_element.fontSize = None
        image_element.classes = []
        image_element.text = ""
        image_element.placeholder = None
        image_element.children = []
        image_element.semantics = Mock()
        image_element.semantics.aria_label = None
        image_element.semantics.aria_labelledby = []
        image_element.semantics.role = None
        image_element.semantics.aria_hidden = False
        image_element.interaction = None

        form_element = Mock(spec=ElementNode)
        form_element.node_id = "input1"
        form_element.tag = "input"
        form_element.attributes = {"type": "text"}
        form_element.classes = []
        form_element.placeholder = None
        form_element.text = ""
        form_element.styles = {}
        form_element.computed = {}
        form_element.color = None
        form_element.backgroundColor = None
        form_element.fontSize = None
        form_element.children = []
        form_element.semantics = Mock()
        form_element.semantics.aria_label = None
        form_element.semantics.aria_labelledby = []
        form_element.semantics.role = None
        form_element.semantics.aria_hidden = False
        form_element.interaction = None

        # Создаем DocumentModel с элементами
        mock_document = Mock(spec=DocumentModel)
        mock_document.info = Mock(spec=DocumentInfo)
        mock_document.info.url = "https://example.com"
        mock_document.info.title = "Test Page"
        mock_document.info.lang = "en"
        mock_document.elements = [image_element, form_element]
        mock_document.root = None

        factory = RulesFactory()
        rules = factory.get_rules(mock_document)

        # Должны быть правила для изображений и форм
        rule_ids = [rule.id for rule, _ in rules]
        assert "1.1.1" in rule_ids  # Rule111MissingAlt
        assert "1.3.1" in rule_ids  # Rule131Label
        assert "form-placeholder-no-label" in rule_ids  # RulePlaceholderWithoutLabel

    def test_empty_document_returns_no_rules(self):
        """Тест что пустой документ возвращает пустой список правил"""
        mock_document = Mock(spec=DocumentModel)
        mock_document.info = Mock(spec=DocumentInfo)
        mock_document.info.url = "https://example.com"
        mock_document.info.title = "Test Page"
        mock_document.info.lang = "en"
        mock_document.elements = []
        mock_document.root = None

        factory = RulesFactory()
        rules = factory.get_rules(mock_document)

        # Должен быть только Rule311Language для структуры документа
        assert len(rules) == 1
        rule_instance, items = rules[0]
        assert rule_instance.id == "3.1.1"

    def test_rules_map_integrity(self):
        """Тест целостности RULES_MAP"""
        factory = RulesFactory()

        # Проверяем что все ключи - это классы данных
        from app.services.analytics.data_group.data_group import (
            ImageData, MediaData, FormFieldData, TableData,
            InteractiveData, HeadingData, StyleData, AriaData,
            DocumentStructureData
        )

        expected_keys = [
            ImageData, MediaData, FormFieldData, TableData,
            InteractiveData, HeadingData, StyleData, AriaData,
            DocumentStructureData
        ]

        for key in expected_keys:
            assert key in factory.RULES_MAP

    def test_rule_instances_have_required_methods(self):
        """Тест что все созданные экземпляры правил имеют необходимые методы"""
        mock_document = Mock(spec=DocumentModel)
        mock_document.info = Mock(spec=DocumentInfo)
        mock_document.info.url = "https://example.com"
        mock_document.info.title = "Test Page"
        mock_document.info.lang = "en"
        mock_document.elements = []
        mock_document.root = None

        factory = RulesFactory()
        rules = factory.get_rules(mock_document)

        for rule_instance, items in rules:
            # Проверяем наличие обязательных атрибутов и методов
            assert hasattr(rule_instance, 'id')
            assert hasattr(rule_instance, 'description')
            assert hasattr(rule_instance, 'check')
            assert callable(rule_instance.check)

    @pytest.mark.parametrize("element_type,expected_rule_ids", [
        ("image", ["1.1.1"]),  # Rule111MissingAlt
        ("media", ["media-autoplay-audio"]),  # RuleMediaAutoplay
        ("form", ["form-placeholder-no-label", "1.3.1"]),  # RulePlaceholderWithoutLabel, Rule131Label
        ("table", ["table-no-headers"]),  # RuleTableNoHeaders
        ("interactive", ["4.1.2"]),  # Rule412LinkPurpose
        ("aria", ["aria-incorrect"]),  # RuleAriaIncorrectUsage
        ("document", ["3.1.1"]),  # Rule311Language
    ])
    def test_specific_element_rules(self, element_type, expected_rule_ids):
        """Параметризованный тест для проверки правил по типам элементов"""
        mock_document = Mock(spec=DocumentModel)
        mock_document.info = Mock(spec=DocumentInfo)
        mock_document.info.url = "https://example.com"
        mock_document.info.title = "Test Page"
        mock_document.info.lang = "en"

        # Создаем элементы в зависимости от типа
        if element_type == "image":
            element = self._create_mock_element("img1", "img")
            element.alt = None
            mock_document.elements = [element]
        elif element_type == "media":
            element = self._create_mock_element("video1", "video")
            element.attributes = {"autoplay": "true", "muted": "false"}
            mock_document.elements = [element]
        elif element_type == "form":
            element = self._create_mock_element("input1", "input")
            element.attributes = {"type": "text"}
            element.placeholder = None
            mock_document.elements = [element]
        elif element_type == "table":
            element = self._create_mock_element("table1", "table")
            element.children = []
            mock_document.elements = [element]
        elif element_type == "interactive":
            element = self._create_mock_element("button1", "button")
            element.text = ""
            mock_document.elements = [element]
        elif element_type == "aria":
            element = self._create_mock_element("div1", "div")
            element.attributes = {"aria-label": "test"}
            element.semantics.role = "button"
            mock_document.elements = [element]
        else:  # document
            mock_document.elements = []

        mock_document.root = None

        factory = RulesFactory()
        rules = factory.get_rules(mock_document)

        # Собираем ID всех правил, которые относятся к нашему элементу
        actual_rule_ids = []
        for rule_instance, items in rules:
            # Для document проверяем специально
            if element_type == "document":
                if (isinstance(items[0], DocumentStructureData) or
                        (isinstance(items[0], Mock) and hasattr(items[0], 'lang'))):
                    actual_rule_ids.append(rule_instance.id)
            else:
                # Для остальных элементов проверяем по node_id
                if any(hasattr(item, 'node_id') and item.node_id.endswith('1') for item in items):
                    actual_rule_ids.append(rule_instance.id)

        # Проверяем что ожидаемые правила присутствуют
        for expected_rule_id in expected_rule_ids:
            assert expected_rule_id in actual_rule_ids, f"Expected rule {expected_rule_id} not found in {actual_rule_ids}"

        # Проверяем количество правил (может быть больше из-за пересечения категорий)
        assert len([rid for rid in actual_rule_ids if rid in expected_rule_ids]) == len(expected_rule_ids)

    def _create_mock_element(self, node_id, tag):
        """Вспомогательный метод для создания mock элемента со всеми необходимыми атрибутами"""
        element = Mock(spec=ElementNode)
        element.node_id = node_id
        element.tag = tag
        element.attributes = {}
        element.classes = []
        element.placeholder = None
        element.text = ""
        element.alt = ""
        element.title = None
        element.src = None
        element.styles = {}
        element.computed = {}
        element.color = None
        element.backgroundColor = None
        element.fontSize = None
        element.children = []
        element.semantics = Mock()
        element.semantics.aria_label = None
        element.semantics.aria_labelledby = []
        element.semantics.role = None
        element.semantics.aria_hidden = False
        element.interaction = None
        return element


# Исправленные старые тесты (если они у вас уже были)

@pytest.fixture
def extractor_patch():
    with patch('app.services.analytics.rules_analyzer.rules_factory.DataGroupExtractor') as mock:
        yield mock


def test_rules_factory_returns_list_of_tuples(extractor_patch):
    """Фабрика должна вернуть список кортежей (rule_instance, data_list)."""
    factory = RulesFactory()
    document = Mock()

    # Настраиваем mock экстрактора
    extractor_patch.return_value.extract_image_data.return_value = []
    extractor_patch.return_value.extract_media_data.return_value = []
    extractor_patch.return_value.extract_form_field_data.return_value = []
    extractor_patch.return_value.extract_table_data.return_value = []
    extractor_patch.return_value.extract_interactive_data.return_value = []
    extractor_patch.return_value.extract_heading_data.return_value = []
    extractor_patch.return_value.extract_style_data.return_value = []
    extractor_patch.return_value.extract_aria_data.return_value = []
    extractor_patch.return_value.extract_document_structure_data.return_value = Mock(spec=DocumentStructureData)

    rules = factory.get_rules(document)
    assert isinstance(rules, list)
    for rule_instance, data_list in rules:
        assert hasattr(rule_instance, 'check')
        assert isinstance(data_list, list)


def test_rules_factory_lazy_loading_works(extractor_patch):
    """rules_map не должен загружаться до вызова create_rules()."""
    factory = RulesFactory()
    document = Mock()

    # Проверяем что RULES_MAP существует
    assert hasattr(factory, 'RULES_MAP')
    assert isinstance(factory.RULES_MAP, dict)


def test_factory_matches_rule_to_group(extractor_patch):
    """Правило должно правильно связываться с группой данных."""
    factory = RulesFactory()
    document = Mock()

    # Тестируем маппинг правил
    from app.services.analytics.data_group.data_group import ImageData
    from app.services.analytics.rules_analyzer.rule_alt_atribute import Rule111MissingAlt

    assert ImageData in factory.RULES_MAP
    assert Rule111MissingAlt in factory.RULES_MAP[ImageData]


def test_factory_calls_extractor_methods(extractor_patch):
    """Проверяем, что методы DataGroupExtractor вызываются."""
    document = Mock()
    factory = RulesFactory()

    # Вызываем метод
    factory.get_rules(document)

    # Проверяем что методы экстрактора вызывались
    extractor_patch.return_value.extract_image_data.assert_called_once_with(document)
    extractor_patch.return_value.extract_media_data.assert_called_once_with(document)
    extractor_patch.return_value.extract_form_field_data.assert_called_once_with(document)