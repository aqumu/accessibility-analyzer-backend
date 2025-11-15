from typing import List, Optional
from app.services.accessibility.analytics.json_parser.models import ElementNode, DocumentModel  # Предполагается, что ElementNode и DocumentModel определены в model.py


# --- Группы данных для проверок ---

class ImageData:
    """
    Данные для проверки изображений (alt, src, title).
    """

    def __init__(self, node: ElementNode):
        self.node_id = node.node_id
        self.tag = node.tag
        self.alt = node.alt
        # Ищем src в attributes, так как его нет в полях ElementNode напрямую
        self.src = node.attributes.get('src')
        self.title = node.title
        self.attributes = node.attributes
        # Дополнительно: проверим, является ли изображение содержательным
        self.is_content_image = node.alt is not None and node.alt.strip() != "" or self.title is not None

    def __repr__(self):
        return f"ImageData(node_id='{self.node_id}', tag='{self.tag}', has_alt={self.alt is not None}, has_title={self.title is not None})"


class FormFieldData:
    """
    Данные для проверки полей форм (input, textarea, select).
    """

    def __init__(self, node: ElementNode):
        self.node_id = node.node_id
        self.tag = node.tag
        self.attributes = node.attributes
        self.classes = node.classes
        self.placeholder = node.placeholder
        self.text = node.text
        # Попробуем найти связанный label (упрощённо: проверим наличие aria-label, aria-labelledby, или placeholder)
        self.aria_label = node.semantics.aria_label if node.semantics else None
        self.aria_labelledby = node.semantics.aria_labelledby if node.semantics else []
        self.has_explicit_label = self._check_for_explicit_label(node)

    def _check_for_explicit_label(self, node: ElementNode) -> bool:
        # Проверка: есть ли id у этого поля?
        field_id = node.attributes.get('id')
        if not field_id:
            return False
        # В реальности нужно искать по всему документу элемент <label for="{field_id}">
        # Для DTO это сложно, но можно сохранить id и передать в алгоритм проверки
        # или хранить ссылку на связанный label, если парсер её нашёл
        # Пока возвращаем False, но алгоритм проверки будет искать label по field_id
        return False

    def __repr__(self):
        return f"FormFieldData(node_id='{self.node_id}', tag='{self.tag}', has_placeholder={self.placeholder is not None}, has_aria_label={self.aria_label is not None})"


class InteractiveData:
    """
    Данные для проверки интерактивных элементов (кнопки, ссылки).
    """

    def __init__(self, node: ElementNode):
        self.node_id = node.node_id
        self.tag = node.tag
        self.text = node.text
        self.attributes = node.attributes
        self.classes = node.classes
        self.aria_label = node.semantics.aria_label if node.semantics else None
        self.aria_hidden = node.semantics.aria_hidden if node.semantics else False
        # tabindex может быть в interaction или в attributes
        self.tabindex = getattr(node.interaction, 'tabindex', None) if node.interaction else node.attributes.get(
            'tabindex')
        self.styles = node.styles  # Для проверки outline: none
        self.role = node.semantics.role if node.semantics else None
        # Проверка на пустую ссылку
        self.is_empty_link = self.tag == 'a' and not self.text.strip() and not self.aria_label and not self.attributes.get(
            'aria-label')

    def __repr__(self):
        return f"InteractiveData(node_id='{self.node_id}', tag='{self.tag}', text='{self.text[:20]}...', has_aria_label={self.aria_label is not None}, tabindex={self.tabindex})"


class StyleData:
    """
    Данные для проверки визуальных стилей (контраст, фокус).
    """

    def __init__(self, node: ElementNode):
        self.node_id = node.node_id
        self.tag = node.tag
        self.text = node.text
        self.color = node.color
        self.backgroundColor = node.backgroundColor
        self.fontSize = node.fontSize
        self.styles = node.styles  # Может содержать outline: none и другие стили
        self.computed = node.computed  # Полные вычисленные стили

    def __repr__(self):
        return f"StyleData(node_id='{self.node_id}', tag='{self.tag}', has_color={self.color is not None}, has_bg_color={self.backgroundColor is not None})"


class MediaData:
    """
    Данные для проверки медиа (video, audio, iframe).
    """

    def __init__(self, node: ElementNode):
        self.node_id = node.node_id
        self.tag = node.tag
        self.attributes = node.attributes
        self.title = node.title
        # src для iframe или media ищем в attributes
        self.src = node.attributes.get('src')
        # autoplay и muted ищем в attributes
        self.autoplay = node.attributes.get('autoplay')  # Может быть 'true', True, или просто наличие атрибута
        self.muted = node.attributes.get('muted')

    def __repr__(self):
        return f"MediaData(node_id='{self.node_id}', tag='{self.tag}', has_title={self.title is not None}, has_autoplay={self.autoplay is not None})"


class HeadingData:
    """
    Данные для проверки заголовков (h1-h6).
    """

    def __init__(self, node: ElementNode):
        self.node_id = node.node_id
        self.tag = node.tag
        self.text = node.text
        self.attributes = node.attributes

    def __repr__(self):
        return f"HeadingData(node_id='{self.node_id}', tag='{self.tag}', text='{self.text[:30]}...')"


class TableData:
    """
    Данные для проверки таблиц (table, th, td).
    """

    def __init__(self, node: ElementNode):
        self.node_id = node.node_id
        self.tag = node.tag
        self.attributes = node.attributes
        # Используем дочерние элементы из DTO
        self.children = node.children
        self.text = node.text

    def __repr__(self):
        return f"TableData(node_id='{self.node_id}', tag='{self.tag}', has_children={len(self.children) > 0})"


class AriaData:
    """
    Данные для проверки ARIA-атрибутов и ролей.
    """

    def __init__(self, node: ElementNode):
        self.node_id = node.node_id
        self.tag = node.tag
        self.attributes = node.attributes
        self.semantics = node.semantics
        self.role = node.semantics.role if node.semantics else None
        self.aria_hidden = node.semantics.aria_hidden if node.semantics else False
        # Проверим, есть ли ARIA-атрибуты в attributes (например, aria-hidden="false")
        self.raw_aria_attrs = {k: v for k, v in node.attributes.items() if k.startswith('aria-')}

    def __repr__(self):
        return f"AriaData(node_id='{self.node_id}', tag='{self.tag}', role='{self.role}', has_raw_aria_attrs={bool(self.raw_aria_attrs)})"


class DocumentStructureData:
    """
    Данные для проверки общей структуры документа.
    """

    def __init__(self, doc_model: DocumentModel):
        self.url = doc_model.info.url
        self.title = doc_model.info.title
        self.lang = doc_model.info.lang
        self.elements = doc_model.elements
        self.root = doc_model.root

    def __repr__(self):
        return f"DocumentStructureData(url='{self.url}', lang='{self.lang}', total_elements={len(self.elements)})"


# --- Модуль группировки данных ---
class DataGroupExtractor:
    """
    Модуль для извлечения и группировки данных из DocumentModel
    для передачи в алгоритмы проверки доступности.
    """

    @staticmethod
    def extract_image_data(doc_model: DocumentModel) -> List[ImageData]:
        """Извлекает данные для проверки изображений."""
        images = []
        for elem in doc_model.elements:
            if elem.tag.lower() in ('img', 'image'):
                images.append(ImageData(elem))
        return images

    @staticmethod
    def extract_form_field_data(doc_model: DocumentModel) -> List[FormFieldData]:
        """Извлекает данные для проверки полей форм."""
        fields = []
        for elem in doc_model.elements:
            if elem.tag.lower() in ('input', 'textarea', 'select'):
                fields.append(FormFieldData(elem))
        return fields

    @staticmethod
    def extract_interactive_data(doc_model: DocumentModel) -> List[InteractiveData]:
        """Извлекает данные для проверки интерактивных элементов."""
        interactive = []
        for elem in doc_model.elements:
            if elem.tag.lower() in ('button', 'a', 'input', 'textarea', 'select', 'area', 'summary'):
                interactive.append(InteractiveData(elem))
        return interactive

    @staticmethod
    def extract_style_data(doc_model: DocumentModel) -> List[StyleData]:
        """Извлекает данные для проверки стилей (контраст, фокус)."""
        styles = []
        for elem in doc_model.elements:
            # Проверяем, есть ли у элемента текст или цвета для анализа
            if elem.text or elem.color or elem.backgroundColor:
                styles.append(StyleData(elem))
        return styles

    @staticmethod
    def extract_media_data(doc_model: DocumentModel) -> List[MediaData]:
        """Извлекает данные для проверки медиа."""
        media = []
        for elem in doc_model.elements:
            if elem.tag.lower() in ('video', 'audio', 'iframe'):
                media.append(MediaData(elem))
        return media

    @staticmethod
    def extract_heading_data(doc_model: DocumentModel) -> List[HeadingData]:
        """Извлекает данные для проверки заголовков."""
        headings = []
        for elem in doc_model.elements:
            if elem.tag.lower() in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
                headings.append(HeadingData(elem))
        return headings

    @staticmethod
    def extract_table_data(doc_model: DocumentModel) -> List[TableData]:
        """Извлекает данные для проверки таблиц."""
        tables = []
        for elem in doc_model.elements:
            if elem.tag.lower() in ('table', 'th', 'td', 'tr'):
                tables.append(TableData(elem))
        return tables

    @staticmethod
    def extract_aria_data(doc_model: DocumentModel) -> List[AriaData]:
        """Извлекает данные для проверки ARIA."""
        aria_data = []
        for elem in doc_model.elements:
            # Проверяем, есть ли у элемента ARIA-атрибуты или семантика
            if (elem.semantics and (elem.semantics.role or elem.semantics.aria_hidden is not False)) or \
                    any(k.startswith('aria-') for k in elem.attributes.keys()):
                aria_data.append(AriaData(elem))
        return aria_data

    @staticmethod
    def extract_document_structure_data(doc_model: DocumentModel) -> DocumentStructureData:
        """Извлекает данные для проверки общей структуры документа."""
        return DocumentStructureData(doc_model)

