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
    title: str
    lang: str = "en"  # Язык по умолчанию
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
@dataclass
class ElementNode:
    """
    Основной класс, представляющий элемент DOM.
    Содержит всю информацию об элементе, необходимую для анализа доступности.

    Атрибуты:
        tag (str): HTML тег элемента
        text (Optional[str]): Текстовое содержимое элемента
        alt (Optional[str]): Альтернативный текст (для img и других элементов)
        title (Optional[str]): Атрибут title
        placeholder (Optional[str]): Плейсхолдер (для input, textarea)
        width (Optional[str]): Ширина элемента
        height (Optional[str]): Высота элемента
        top (Optional[str]): Позиция сверху
        left (Optional[str]): Позиция слева
        depth (Optional[int]): Глубина вложенности в DOM (из нового формата)
        num_children (Optional[int]): Количество дочерних элементов (из нового формата)
        fontSize (Optional[str]): Размер шрифта
        fontWeight (Optional[str]): Жирность шрифта
        lineHeight (Optional[str]): Высота строки
        opacity (Optional[str]): Прозрачность
        letterSpacing (Optional[str]): Интервал между буквами
        color (Optional[str]): Цвет текста
        backgroundColor (Optional[str]): Цвет фона
        position (Optional[str]): Позиционирование
        display (Optional[str]): Отображение
        textAlign (Optional[str]): Выравнивание текста
        styles (Dict[str, Any]): Словарь всех стилевых свойств (для удобства)
        computed (Dict[str, Any]): Вычисленные стили (оставлен для расширения)
        pseudo (Dict[str, Any]): Псевдо-элементы (оставлен для расширения)
        semantics (Optional[NodeSemantics]): Семантическая информация
        interaction (Optional[NodeInteraction]): Информация об интерактивности
        layout (Optional[NodeLayout]): Информация о расположении
        form (Optional[FormInfo]): Информация о форме (если элемент формы)
        media (Optional[MediaInfo]): Информация о медиа (если медиа-элемент)
        dom_path (Optional[str]): Путь к элементу в DOM (оставлен для расширения)
        children (List[ElementNode]): Список дочерних элементов
    """
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
    layout: Optional[NodeLayout] = None
    form: Optional[FormInfo] = None
    media: Optional[MediaInfo] = None

    dom_path: Optional[str] = None
    children: List[ElementNode] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ElementNode":
        """
        Создает экземпляр ElementNode из JSON-данных в новом формате.

        Args:
            data (Dict[str, Any]): Словарь с JSON-данными элемента из нового формата

        Returns:
            ElementNode: Экземпляр элемента DOM

        Пример входных данных:
        {
            "tag": "button",
            "text": "Нажми меня",
            "alt": null,
            "title": "Кнопка для отправки формы",
            "placeholder": null,
            "width": "120px",
            "height": "40px",
            "top": "80px",
            "left": "50px",
            "fontSize": "16px",
            "fontWeight": "500",
            "lineHeight": "1.5",
            "opacity": "0.95",
            "letterSpacing": "0.5px",
            "color": "rgb(255, 255, 255)",
            "backgroundColor": "rgb(0, 123, 255)",
            "position": "relative",
            "display": "inline-block",
            "textAlign": "center",
            "depth": 3,
            "num_children": 1
        }
        """
        # Collect data from JSON
        tag = data.get("tag", "")
        text = data.get("text")
        alt = data.get("alt")
        title = data.get("title")
        placeholder = data.get("placeholder")

        width = data.get("width")
        height = data.get("height")
        top = data.get("top")
        left = data.get("left")
        depth = data.get("depth")
        num_children = data.get("num_children")

        font_size = data.get("fontSize")
        font_weight = data.get("fontWeight")
        line_height = data.get("lineHeight")
        opacity = data.get("opacity")
        letter_spacing = data.get("letterSpacing")
        color = data.get("color")
        background_color = data.get("backgroundColor")
        position = data.get("position")
        display = data.get("display")
        text_align = data.get("textAlign")

        all_styles = {
            key: value for key, value in {
                "color": color,
                "backgroundColor": background_color,
                "fontSize": font_size,
                "fontWeight": font_weight,
                "lineHeight": line_height,
                "letterSpacing": letter_spacing,
                "position": position,
                "display": display,
                "textAlign": text_align,
                "width": width,
                "height": height,
                "top": top,
                "left": left,
                "opacity": opacity
            }.items() if value is not None
        }

        semantics = None
        if "semantics" in data:
            semantics = NodeSemantics(**data["semantics"])

        interaction = None
        if "interaction" in data:
            interaction = NodeInteraction(**data["interaction"])

        layout = None
        if "layout" in data:
            layout = NodeLayout(**data["layout"])
        else:
            layout = NodeLayout(depth=depth, num_children=num_children)

        form = None
        if "form" in data:
            form = FormInfo(**data["form"])

        media = None
        if tag in ["img", "video", "audio", "canvas"]:
            media = MediaInfo(
                alt=alt,
                title=title,
            )

        children = [
            ElementNode.from_json(child_data)
            for child_data in data.get("children", [])
        ]

        return cls(
            tag=tag,
            text=text,
            alt=alt,
            title=title,
            placeholder=placeholder,
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
            styles=all_styles,
            semantics=semantics,
            interaction=interaction,
            layout=layout,
            form=form,
            media=media,
            children=children
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


# ---------------------------
# Document Factory
# ---------------------------
class DocumentFactory:

    @staticmethod
    def load_from_json(data: Dict[str, Any]) -> DocumentModel:
        """
        Создает DocumentModel из JSON-данных в новом формате.

        Args:
            data (Dict[str, Any]): JSON-данные документа в новом формате

        Returns:
            DocumentModel: Модель документа, готовая для анализа доступности

        Пример входных данных:
        {
            "elements": [
                {
                    "tag": "h1",
                    "text": "Главный заголовок",
                    ...
                },
                {
                    "tag": "button",
                    "text": "Кнопка",
                    ...
                }
            ]
        }
        """
        doc_info = DocumentInfo(
            title=data.get("url", "Analyzed Document"),
            lang=data.get("lang", "en"),
            parse_errors=data.get("parse_errors", [])
        )

        elements = [
            ElementNode.from_json(element_data)
            for element_data in data.get("elements", [])
        ]

        root_node = ElementNode(
            tag="virtual_root",
            text="",
            children=elements
        )

        return DocumentModel(
            info=doc_info,
            root=root_node,
            elements=elements
        )