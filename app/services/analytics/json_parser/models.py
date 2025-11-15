from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol


# ---------------------------
# Document info
# ---------------------------
@dataclass
class DocumentInfo:
    """
    Атрибуты:
        title (str): Заголовок документа (например, URL или название страницы)
        lang (str): Язык документа (например, 'en', 'ru')
        parse_errors (List[str]): Список ошибок, возникших при парсинге документа
    """
    url: Optional[str] = None
    title: Optional[str] = None
    lang: Optional[str] = None  # Язык по умолчанию
    parse_errors: List[str] = field(default_factory=list)


# ---------------------------
# Main DOM element
# ---------------------------
class BaseNode(Protocol):
    """
    Протокол, определяющий интерфейс для всех узлов DOM.
    Используется для статической типизации и документирования ожидаемого поведения.

    Атрибуты:
        tag (str): HTML тег элемента (например, 'div', 'button', 'input')
        children (List[ElementNode]): Список дочерних элементов
    """
    tag: str
    children: List[ElementNode]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "BaseNode":
        """
        Метод для создания экземпляра узла из JSON-данных.

        Args:
            data (Dict[str, Any]): Словарь с JSON-данными элемента

        Returns:
            BaseNode: Экземпляр узла DOM
        """
        ...


# ---------------------------
# Util structures
# ---------------------------

@dataclass
class MediaInfo:
    """
    Информация о медиа-элементах (img, video, audio).
    Используется для проверки доступности медиа-контента.

    Атрибуты:
        alt (Optional[str]): Альтернативный текст для изображений
        src (Optional[str]): Источник медиа-файла
        title (Optional[str]): Заголовок/описание элемента
    """
    alt: Optional[str] = None
    src: Optional[str] = None
    title: Optional[str] = None


@dataclass
class NodeStyles:
    """
    Класс для хранения стилевых свойств элемента.
    Используется для анализа визуальной доступности (контрастность, размер шрифта и т.д.).

    Атрибуты:
        color (Optional[str]): Цвет текста (например, 'rgb(33, 37, 41)')
        backgroundColor (Optional[str]): Цвет фона (например, 'rgb(255, 255, 255)')
        fontSize (Optional[str]): Размер шрифта (например, '16px', '1.2em')
        fontWeight (Optional[str]): Жирность шрифта (например, '400', '700')
        lineHeight (Optional[str]): Высота строки (например, '1.2', 'normal')
        letterSpacing (Optional[str]): Интервал между буквами (например, 'normal', '0.5px')
        position (Optional[str]): Позиционирование (например, 'static', 'relative')
        display (Optional[str]): Отображение (например, 'block', 'inline-block')
        textAlign (Optional[str]): Выравнивание текста (например, 'left', 'center')
        width (Optional[str]): Ширина элемента
        height (Optional[str]): Высота элемента
        top (Optional[str]): Позиция сверху
        left (Optional[str]): Позиция слева
        opacity (Optional[str]): Прозрачность (например, '1', '0.95')
    """
    color: Optional[str] = None
    backgroundColor: Optional[str] = None
    fontSize: Optional[str] = None
    fontWeight: Optional[str] = None
    lineHeight: Optional[str] = None
    letterSpacing: Optional[str] = None
    position: Optional[str] = None
    display: Optional[str] = None
    textAlign: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    top: Optional[str] = None
    left: Optional[str] = None
    opacity: Optional[str] = None


@dataclass
class NodeSemantics:
    """
    Класс для хранения семантической информации элемента.
    Используется для анализа доступности через ARIA-атрибуты и семантическую разметку.

    Атрибуты:
        role (Optional[str]): Явная ARIA-роль элемента (например, 'button', 'navigation')
        implicit_role (Optional[str]): Неявная роль, определяемая по тегу
        aria_label (Optional[str]): ARIA-лейбл для элемента
        aria_labelledby (List[str]): Список ID элементов, которые лейблят этот элемент
        aria_describedby (List[str]): Список ID элементов, которые описывают этот элемент
        aria_hidden (Optional[bool]): Является ли элемент скрытым для скринридера
        accessible_name (Optional[str]): Доступное имя элемента (для скринридера)
    """
    role: Optional[str] = None
    implicit_role: Optional[str] = None
    aria_label: Optional[str] = None
    aria_labelledby: List[str] = field(default_factory=list)
    aria_describedby: List[str] = field(default_factory=list)
    aria_hidden: Optional[bool] = False
    accessible_name: Optional[str] = None

@dataclass
class NodeInteraction:
    """
    Класс для хранения информации об интерактивности элемента.
    Используется для проверки клавиатурной навигации и фокуса.

    Атрибуты:
        focusable (Optional[bool]): Может ли элемент получать фокус
        programmable_focusable (Optional[bool]): Может ли элемент получать фокус программно
        tabindex (Optional[int]): Значение атрибута tabindex
        has_click_handler (Optional[bool]): Есть ли обработчик клика
        has_key_handler (Optional[bool]): Есть ли обработчик клавиатуры
    """
    focusable: Optional[bool] = False
    programmable_focusable: Optional[bool] = False
    tabindex: Optional[int] = None
    has_click_handler: Optional[bool] = False
    has_key_handler: Optional[bool] = False


@dataclass
class NodeLayout:
    """
    Класс для хранения информации о расположении элемента.
    Используется для анализа визуального порядка и иерархии.

    Атрибуты:
        order_dom (Optional[int]): Порядок в DOM (0-based индекс)
        order_visual (Optional[int]): Визуальный порядок (по расположению на странице)
        position (Optional[str]): CSS-позиционирование
        coordinates (Optional[Dict[str, int]]): Координаты элемента {'x': int, 'y': int}
        depth (Optional[int]): Глубина вложенности в DOM
        num_children (Optional[int]): Количество дочерних элементов
    """
    order_dom: Optional[int] = None
    order_visual: Optional[int] = None
    position: Optional[str] = None
    coordinates: Optional[Dict[str, int]] = None
    depth: Optional[int] = None
    num_children: Optional[int] = None


@dataclass
class FormInfo:
    """
    Класс для хранения информации о формах и элементах управления.
    Используется для проверки доступности форм.

    Атрибуты:
        type (Optional[str]): Тип элемента формы (например, 'text', 'email', 'submit')
        required (Optional[bool]): Обязательное поле или нет
        label (Optional[str]): Лейбл поля
        label_for (Optional[str]): ID элемента, для которого этот элемент является лейблом
        described_by (List[str]): Список ID элементов, описывающих это поле
        error_messages (List[str]): Сообщения об ошибках для этого поля
    """
    type: Optional[str] = None
    required: Optional[bool] = None
    label: Optional[str] = None
    label_for: Optional[str] = None
    described_by: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)


# ---------------------------
# Основной класс элемента DOM
# ---------------------------
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class ElementNode:
    # --- Основные поля ---
    tag: str

    text: Optional[str] = None
    alt: Optional[str] = None
    title: Optional[str] = None
    placeholder: Optional[str] = None

    width: Optional[str] = None
    height: Optional[str] = None
    top: Optional[str] = None
    left: Optional[str] = None
    depth: Optional[int] = None
    num_children: Optional[int] = None

    fontSize: Optional[str] = None
    fontWeight: Optional[str] = None
    lineHeight: Optional[str] = None
    opacity: Optional[str] = None
    letterSpacing: Optional[str] = None
    color: Optional[str] = None
    backgroundColor: Optional[str] = None
    position: Optional[str] = None
    display: Optional[str] = None
    textAlign: Optional[str] = None

    styles: Dict[str, Any] = field(default_factory=dict)
    computed: Dict[str, Any] = field(default_factory=dict)
    pseudo: Dict[str, Any] = field(default_factory=dict)

    semantics: Optional[NodeSemantics] = None
    interaction: Optional[NodeInteraction] = None
    form: Optional[FormInfo] = None
    media: Optional[MediaInfo] = None

    dom_path: Optional[str] = None

    # --- Иерархия и вспомогательные поля ---
    parent: Optional[ElementNode] = field(default=None, repr=False, compare=False)
    children: List[ElementNode] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    classes: List[str] = field(default_factory=list)
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # -------------------------------------------------
    # Создание из JSON (новый формат парсера)
    # -------------------------------------------------
    @classmethod
    def from_json(cls, data: Dict[str, Any], parent: Optional[ElementNode] = None) -> ElementNode:
        """
        Построить ElementNode из JSON, который возвращает твой парсер.
        Ожидает, что data может содержать:
          - tag, id, classes, text, attributes, computedStyles, children, depth, index, parent_id, pseudo, semantics, interaction, layout, form, media
        """
        tag = data.get("tag", "")
        attributes = dict(data.get("attributes", {}) or {})

        classes = data.get("classes", []) or []
        element_id = data.get("id") or attributes.get("id")  # предпочитаем data["id"] если есть
        text = data.get("text") or attributes.get("text") or ""
        computed_styles = dict(data.get("computedStyles", {}) or {})
        pseudo = dict(data.get("pseudo", {}) or {})

        # Структурные поля
        depth = data.get("depth")
        index = data.get("index")
        parent_id = data.get("parent_id")

        # Количество детей (из данных или посчитать)
        children_data = data.get("children", []) or []
        num_children = data.get("num_children", len(children_data))

        # Извлечение отдельных стилевых свойств (если есть)
        font_size = computed_styles.get("fontSize")
        font_weight = computed_styles.get("fontWeight")
        line_height = computed_styles.get("lineHeight")
        opacity = computed_styles.get("opacity")
        letter_spacing = computed_styles.get("letterSpacing")
        color = computed_styles.get("color")
        background_color = computed_styles.get("backgroundColor")
        position = computed_styles.get("position")
        display = computed_styles.get("display")
        text_align = computed_styles.get("textAlign")

        # Размеры/позиции — сначала из attributes, затем из computedStyles
        width = attributes.get("width") or computed_styles.get("width")
        height = attributes.get("height") or computed_styles.get("height")
        top = attributes.get("top") or computed_styles.get("top")
        left = attributes.get("left") or computed_styles.get("left")

        # Объединяем стили (computedStyles имеет приоритет, но оставляем все)
        styles = {**computed_styles}
        # Доп. поля из attributes (например inline width/height) — добавляем, если существуют
        for key in ("width", "height", "top", "left", "opacity"):
            if attributes.get(key) is not None:
                styles[key] = attributes.get(key)

        # Семантика/interaction/layout/form/media — если есть, пробуем создать/скопировать
        semanticsDict = data.get("semantics")
        semantics = None
        if semanticsDict:
            semantics = NodeSemantics(**semanticsDict)

        interaction = data.get("interaction")
        form = data.get("form")

        # Создаём сам узел
        node = cls(
            tag=tag,
            text=text,
            alt=data.get("alt") or attributes.get("alt"),
            title=data.get("title"),
            placeholder=attributes.get("placeholder"),
            width=width,
            height=height,
            top=top,
            left=left,
            depth=depth,
            num_children=num_children,
            fontSize=font_size,
            fontWeight=font_weight,
            lineHeight=line_height,
            opacity=opacity,
            letterSpacing=letter_spacing,
            color=color,
            backgroundColor=background_color,
            position=position,
            display=display,
            textAlign=text_align,
            styles=styles,
            computed=computed_styles,
            pseudo=pseudo,
            semantics=semantics,
            interaction=interaction,
            form=form,
            dom_path=data.get("dom_path") or (f"{parent.dom_path}/{tag}" if parent and parent.dom_path else None),
            parent=parent,
            children=[],  # заполним ниже
            attributes=attributes,
            classes=classes,
            node_id=element_id or str(uuid.uuid4())
        )

        # Рекурсивно создаём детей и назначаем parent
        for child_data in children_data:
            child_node = cls.from_json(child_data, parent=node)
            node.children.append(child_node)

        # Обновляем num_children, если нужно
        node.num_children = len(node.children)

        return node

    # -------------------------------------------------
    # Получить CSS-like путь (удобно для логов)
    # -------------------------------------------------
    def get_path(self) -> str:
        parts: List[str] = []
        node: Optional[ElementNode] = self
        while node is not None:
            part = node.tag or "?"
            # добавить id или классы если есть
            if node.attributes.get("id"):
                part += f"#{node.attributes.get('id')}"
            elif node.node_id:
                # не выводим UUID всегда — только по желанию; закомментировано по умолчанию
                # part += f"@{node.node_id[:8]}"
                pass

            if node.classes:
                cls_string = ".".join([c for c in node.classes if c])
                if cls_string:
                    part += f".{cls_string}"

            parts.append(part)
            node = node.parent
        return " > ".join(reversed(parts))

    # -------------------------------------------------
    # Читаемый вывод для логов/тестов
    # -------------------------------------------------
    def __repr__(self) -> str:
        parent_tag = self.parent.tag if self.parent else None
        text_preview = (self.text[:30] + "...") if self.text and len(self.text) > 30 else (self.text or "")
        return (
            f"ElementNode(tag='{self.tag}', text='{text_preview}', "
            f"children={len(self.children)}, parent='{parent_tag}', id='{self.node_id}')"
        )

# ---------------------------
# Document Model
# ---------------------------
@dataclass
class DocumentModel:
    """
    Модель всего документа (веб-страницы).
    Содержит информацию о документе и все его элементы.

    Атрибуты:
        info (DocumentInfo): Основная информация о документе
        root (ElementNode): Корневой элемент (виртуальный, содержащий все элементы)
        elements (List[ElementNode]): Список всех элементов документа
    """
    info: DocumentInfo
    root: ElementNode
    elements: List[ElementNode] = field(default_factory=list)


class DocumentFactory:

    @staticmethod
    def flatten_tree(node: ElementNode) -> List[ElementNode]:
        """Разворачивает дерево в плоский список."""
        result = [node]
        for child in node.children:
            result.extend(DocumentFactory.flatten_tree(child))
        return result

    @staticmethod
    def load_from_json(data: Dict[str, Any]) -> DocumentModel:
        """
        Загружает DOM из JSON (новый формат)
        и разворачивает дерево в плоскую структуру.
        """

        # --- META ---
        meta = data.get("meta", {})

        doc_info = DocumentInfo(
            url = meta.get("url"),
            title=meta.get("title", "Analyzed Document"),
            lang=meta.get("lang", "en"),
            parse_errors=data.get("parse_errors", [])
        )

        # --- Root HTML elements ---
        root_nodes = [
            ElementNode.from_json(element_data)
            for element_data in data.get("root_elements", [])
        ]

        # Создаем виртуальный корень
        virtual_root = ElementNode(
            tag="virtual_root",
            text="",
            children=root_nodes
        )

        # --- Flatten ---
        elements_flat = DocumentFactory.flatten_tree(virtual_root)

        return DocumentModel(
            info=doc_info,
            root=virtual_root,
            elements=elements_flat
        )
