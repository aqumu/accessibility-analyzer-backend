import pytest
from app.services.analytics.json_parser.models import (
    DocumentInfo,
    MediaInfo,
    NodeStyles,
    NodeSemantics,
    NodeInteraction,
    NodeLayout,
    FormInfo,
    ElementNode,
    DocumentModel,
    DocumentFactory
)


class TestDocumentInfo:
    def test_document_info_creation(self):
        info = DocumentInfo(title="Test Page", lang="en", url="https://google.com")
        assert info.title == "Test Page"
        assert info.lang == "en"
        assert info.parse_errors == []
        assert info.url == "https://google.com"

    def test_document_info_with_errors(self):
        errors = ["Error 1", "Error 2"]
        info = DocumentInfo(title="Test Page", lang="ru", parse_errors=errors)
        assert info.parse_errors == errors

    def test_document_info_defaults(self):
        info = DocumentInfo(title="Test Page")
        assert info.lang is None
        assert info.parse_errors == []


class TestMediaInfo:
    def test_media_info_creation(self):
        media = MediaInfo(alt="Alternative text", src="image.jpg", title="Image title")
        assert media.alt == "Alternative text"
        assert media.src == "image.jpg"
        assert media.title == "Image title"

    def test_media_info_defaults(self):
        media = MediaInfo()
        assert media.alt is None
        assert media.src is None
        assert media.title is None


class TestNodeStyles:
    def test_node_styles_creation(self):
        styles = NodeStyles(
            color="rgb(255, 0, 0)",
            fontSize="16px",
            fontWeight="bold",
            backgroundColor="rgb(255, 255, 255)"
        )
        assert styles.color == "rgb(255, 0, 0)"
        assert styles.fontSize == "16px"
        assert styles.fontWeight == "bold"
        assert styles.backgroundColor == "rgb(255, 255, 255)"

    def test_node_styles_defaults(self):
        styles = NodeStyles()
        assert styles.color is None
        assert styles.backgroundColor is None
        assert styles.fontSize is None


class TestNodeSemantics:
    def test_node_semantics_creation(self):
        semantics = NodeSemantics(
            role="button",
            aria_label="Submit button",
            aria_hidden=False,
            accessible_name="Submit"
        )
        assert semantics.role == "button"
        assert semantics.aria_label == "Submit button"
        assert semantics.aria_hidden is False
        assert semantics.accessible_name == "Submit"

    def test_node_semantics_defaults(self):
        semantics = NodeSemantics()
        assert semantics.role is None
        assert semantics.aria_label is None
        assert semantics.aria_hidden is False
        assert semantics.aria_labelledby == []
        assert semantics.aria_describedby == []


class TestNodeInteraction:
    def test_node_interaction_creation(self):
        interaction = NodeInteraction(
            focusable=True,
            programmable_focusable=True,
            tabindex=0,
            has_click_handler=True
        )
        assert interaction.focusable is True
        assert interaction.programmable_focusable is True
        assert interaction.tabindex == 0
        assert interaction.has_click_handler is True

    def test_node_interaction_defaults(self):
        interaction = NodeInteraction()
        assert interaction.focusable is False
        assert interaction.programmable_focusable is False
        assert interaction.tabindex is None
        assert interaction.has_click_handler is False


class TestNodeLayout:
    def test_node_layout_creation(self):
        coordinates = {"x": 100, "y": 200}
        layout = NodeLayout(
            order_dom=1,
            position="relative",
            coordinates=coordinates,
            depth=2,
            num_children=3
        )
        assert layout.order_dom == 1
        assert layout.position == "relative"
        assert layout.coordinates == coordinates
        assert layout.depth == 2
        assert layout.num_children == 3

    def test_node_layout_defaults(self):
        layout = NodeLayout()
        assert layout.order_dom is None
        assert layout.position is None
        assert layout.coordinates is None
        assert layout.depth is None
        assert layout.num_children is None


class TestFormInfo:
    def test_form_info_creation(self):
        described_by = ["error1", "error2"]
        error_messages = ["Field is required", "Invalid format"]

        form_info = FormInfo(
            type="email",
            required=True,
            label="Email Address",
            described_by=described_by,
            error_messages=error_messages
        )
        assert form_info.type == "email"
        assert form_info.required is True
        assert form_info.label == "Email Address"
        assert form_info.described_by == described_by
        assert form_info.error_messages == error_messages

    def test_form_info_defaults(self):
        form_info = FormInfo()
        assert form_info.type is None
        assert form_info.required is None
        assert form_info.label is None
        assert form_info.described_by == []
        assert form_info.error_messages == []


class TestElementNode:
    def test_element_node_creation(self):
        node = ElementNode(tag="div", text="Hello World")
        assert node.tag == "div"
        assert node.text == "Hello World"
        assert node.children == []

    def test_element_node_from_json_basic(self):
        json_data = {
            "tag": "h1",
            "text": "Main Title",
            "alt": None,
            "title": "Main Title",
            "placeholder": None,
            "attributes": {
                "width": "720px",
                "height": "48px",
                "top": "20px",
                "left": "50px"
            },
            "computedStyles": {
                "fontSize": "32px",
                "fontWeight": "700",
                "lineHeight": "1.2",
                "opacity": "1",
                "letterSpacing": "normal",
                "color": "rgb(33, 37, 41)",
                "backgroundColor": "rgb(255, 255, 255)",
                "position": "static",
                "display": "block",
                "textAlign": "left"
            },
            "depth": 2,
            "num_children": 0
        }

        node = ElementNode.from_json(json_data)

        assert node.tag == "h1"
        assert node.text == "Main Title"
        assert node.alt is None
        assert node.title == "Main Title"
        assert node.placeholder is None
        assert node.width == "720px"
        assert node.height == "48px"
        assert node.top == "20px"
        assert node.left == "50px"
        assert node.depth == 2
        assert node.num_children == 0
        assert node.fontSize == "32px"
        assert node.fontWeight == "700"
        assert node.lineHeight == "1.2"
        assert node.opacity == "1"
        assert node.letterSpacing == "normal"
        assert node.color == "rgb(33, 37, 41)"
        assert node.backgroundColor == "rgb(255, 255, 255)"
        assert node.position == "static"
        assert node.display == "block"
        assert node.textAlign == "left"

        assert node.styles["color"] == "rgb(33, 37, 41)"
        assert node.styles["backgroundColor"] == "rgb(255, 255, 255)"
        assert node.styles["fontSize"] == "32px"
        assert node.styles["fontWeight"] == "700"
        assert node.styles["lineHeight"] == "1.2"
        assert node.styles["letterSpacing"] == "normal"
        assert node.styles["position"] == "static"
        assert node.styles["display"] == "block"
        assert node.styles["textAlign"] == "left"
        assert node.styles["width"] == "720px"
        assert node.styles["height"] == "48px"
        assert node.styles["top"] == "20px"
        assert node.styles["left"] == "50px"
        assert node.styles["opacity"] == "1"

        assert node.semantics is None
        assert node.interaction is None
        assert node.form is None
        assert node.media is None
        assert node.dom_path is None
        assert node.children == []

    """
    def test_element_node_from_json_with_all_extended_data(self):
        json_data = {
            "tag": "input",
            "text": "",
            "alt": "Поле для ввода email",
            "title": "Введите ваш адрес электронной почты",
            "placeholder": "user@example.com",
            "width": "300px",
            "height": "38px",
            "top": "140px",
            "left": "auto",
            "fontSize": "16px",
            "fontWeight": "400",
            "lineHeight": "normal",
            "opacity": "1",
            "letterSpacing": "normal",
            "color": "rgb(73, 80, 87)",
            "backgroundColor": "rgb(255, 255, 255)",
            "position": "static",
            "display": "block",
            "textAlign": "start",
            "depth": 3,
            "num_children": 0,
            "semantics": {
                "role": "textbox",
                "aria_label": "Email input",
                "aria_hidden": False,
                "accessible_name": "Email"
            },
            "interaction": {
                "focusable": True,
                "programmable_focusable": True,
                "tabindex": 0,
                "has_click_handler": False,
                "has_key_handler": True
            },
            "layout": {
                "order_dom": 1,
                "order_visual": 2,
                "position": "static"
            },
            "form": {
                "type": "email",
                "required": True,
                "label": "Email",
                "described_by": ["error1"],
                "error_messages": ["Required field"]
            }
        }

        node = ElementNode.from_json(json_data)

        assert node.tag == "input"
        assert node.text == ""
        assert node.alt == "Поле для ввода email"
        assert node.title == "Введите ваш адрес электронной почты"
        assert node.placeholder == "user@example.com"
        assert node.width == "300px"
        assert node.height == "38px"
        assert node.top == "140px"
        assert node.left == "auto"
        assert node.depth == 3
        assert node.num_children == 0
        assert node.fontSize == "16px"
        assert node.fontWeight == "400"
        assert node.lineHeight == "normal"
        assert node.opacity == "1"
        assert node.letterSpacing == "normal"
        assert node.color == "rgb(73, 80, 87)"
        assert node.backgroundColor == "rgb(255, 255, 255)"
        assert node.position == "static"
        assert node.display == "block"
        assert node.textAlign == "start"

        assert node.semantics is not None
        assert node.semantics.role == "textbox"
        assert node.semantics.aria_label == "Email input"
        assert node.semantics.aria_hidden is False
        assert node.semantics.accessible_name == "Email"

        assert node.interaction is not None
        assert node.interaction.focusable is True
        assert node.interaction.programmable_focusable is True
        assert node.interaction.tabindex == 0
        assert node.interaction.has_click_handler is False
        assert node.interaction.has_key_handler is True

        assert node.layout is not None
        assert node.layout.order_dom == 1
        assert node.layout.order_visual == 2
        assert node.layout.position == "static"
        assert node.layout.depth == 3
        assert node.layout.num_children == 0

        assert node.form is not None
        assert node.form.type == "email"
        assert node.form.required is True
        assert node.form.label == "Email"
        assert node.form.described_by == ["error1"]
        assert node.form.error_messages == ["Required field"]

        assert node.media is None
        assert node.dom_path is None
        assert node.children == []
        """

    # def test_element_node_from_json_with_media(self):
    #     json_data = {
    #         "tag": "img",
    #         "text": "",
    #         "alt": "Description of image",
    #         "title": "Image title",
    #         "placeholder": None,
    #         "width": "300px",
    #         "height": "200px",
    #         "top": "100px",
    #         "left": "50px",
    #         "fontSize": "16px",
    #         "fontWeight": "400",
    #         "lineHeight": "normal",
    #         "opacity": "1",
    #         "letterSpacing": "normal",
    #         "color": "rgb(0, 0, 0)",
    #         "backgroundColor": "rgb(255, 255, 255)",
    #         "position": "static",
    #         "display": "block",
    #         "textAlign": "left",
    #         "depth": 1,
    #         "num_children": 0
    #     }
    #
    #     node = ElementNode.from_json(json_data)
    #
    #     assert node.media is not None
    #     assert node.media.alt == "Description of image"
    #     assert node.media.title == "Image title"
    #     assert node.media.src is None

    def test_element_node_from_json_with_semantics(self):
        json_data = {
            "tag": "button",
            "text": "Click me",
            "alt": None,
            "title": "Button title",
            "placeholder": None,
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
            "num_children": 1,
            "semantics": {
                "role": "button",
                "aria_label": "Submit form",
                "aria_hidden": False,
                "aria_labelledby": ["label1", "label2"],
                "aria_describedby": ["desc1"],
                "accessible_name": "Submit button"
            }
        }

        node = ElementNode.from_json(json_data)

        assert node.semantics is not None
        assert node.semantics.role == "button"
        assert node.semantics.aria_label == "Submit form"
        assert node.semantics.aria_hidden is False
        assert node.semantics.aria_labelledby == ["label1", "label2"]
        assert node.semantics.aria_describedby == ["desc1"]
        assert node.semantics.accessible_name == "Submit button"

    def test_element_node_with_children(self):
        json_data = {
            "tag": "div",
            "text": "Parent",
            "alt": None,
            "title": None,
            "placeholder": None,
            "width": "auto",
            "height": "auto",
            "top": "0px",
            "left": "0px",
            "computedStyles": {
                "fontSize": "16px",
                "fontWeight": "400",
                "lineHeight": "normal",
                "opacity": "1",
                "letterSpacing": "normal",
                "color": "rgb(0, 0, 0)",
                "backgroundColor": "rgb(255, 255, 255)",
                "position": "static",
                "display": "block",
                "textAlign": "left"
            },
            "depth": 0,
            "num_children": 1,
            "children": [
                {
                    "tag": "span",
                    "text": "Child",
                    "alt": None,
                    "title": None,
                    "placeholder": None,
                    "width": "auto",
                    "height": "auto",
                    "top": "0px",
                    "left": "0px",
                    "computedStyles": {
                         "fontSize": "14px",
                        "fontWeight": "400",
                        "lineHeight": "normal",
                        "opacity": "1",
                        "letterSpacing": "normal",
                        "color": "rgb(0, 0, 0)",
                        "backgroundColor": "rgb(255, 255, 255)",
                        "position": "static",
                        "display": "inline",
                        "textAlign": "left",
                    },
                    "depth": 1,
                    "num_children": 0
                }
            ]
        }

        node = ElementNode.from_json(json_data)

        assert len(node.children) == 1
        assert node.children[0].tag == "span"
        assert node.children[0].text == "Child"
        assert node.children[0].fontSize == "14px"
        assert node.children[0].display == "inline"

    def test_element_node_from_json_with_missing_fields(self):
        json_data = {
            "tag": "div",
            "text": "Minimal data",
            "alt": None,
            "title": None,
            "placeholder": None,
            "width": None,
            "height": None,
            "top": None,
            "left": None,
            "fontSize": None,
            "fontWeight": None,
            "lineHeight": None,
            "opacity": None,
            "letterSpacing": None,
            "color": None,
            "backgroundColor": None,
            "position": None,
            "display": None,
            "textAlign": None,
            "depth": None,
            "num_children": None
        }

        node = ElementNode.from_json(json_data)

        assert node.tag == "div"
        assert node.text == "Minimal data"
        assert node.alt is None
        assert node.title is None
        assert node.placeholder is None
        assert node.width is None
        assert node.height is None
        assert node.top is None
        assert node.left is None
        assert node.depth is None
        assert node.num_children == 0
        assert node.fontSize is None
        assert node.fontWeight is None
        assert node.lineHeight is None
        assert node.opacity is None
        assert node.letterSpacing is None
        assert node.color is None
        assert node.backgroundColor is None
        assert node.position is None
        assert node.display is None
        assert node.textAlign is None

        assert node.styles == {}
        assert node.semantics is None
        assert node.interaction is None
        assert node.form is None
        assert node.media is None
        assert node.dom_path is None
        assert node.children == []


class TestDocumentFactory:
    def test_load_from_json(self):
        json_data = {
            "meta": {
                "url": "https://example.com",
            },
            "root_elements": [
                {
                    "tag": "h1",
                    "text": "Main Title",
                    "alt": None,
                    "title": "Main Title",
                    "placeholder": None,
                    "width": "720px",
                    "height": "48px",
                    "top": "20px",
                    "left": "50px",
                    "fontSize": "32px",
                    "fontWeight": "700",
                    "lineHeight": "1.2",
                    "opacity": "1",
                    "letterSpacing": "normal",
                    "color": "rgb(33, 37, 41)",
                    "backgroundColor": "rgb(255, 255, 255)",
                    "position": "static",
                    "display": "block",
                    "textAlign": "left",
                    "depth": 2,
                    "num_children": 0
                },
                {
                    "tag": "button",
                    "text": "Click me",
                    "alt": None,
                    "title": "Button title",
                    "placeholder": None,
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
            ]
        }

        document = DocumentFactory.load_from_json(json_data)

        assert isinstance(document.info, DocumentInfo)
        assert document.info.url == "https://example.com"

        assert len(document.root.children) == 2
        assert document.root.children[0].tag == "h1"
        assert document.root.children[1].tag == "button"

        assert len(document.elements) == 3
        assert document.elements[1].text == "Main Title"
        assert document.elements[2].text == "Click me"

    def test_load_from_json_empty_elements(self):
        json_data = {
            "meta": {
                "url": "https://empty.com",
            },
            "root_elements": []
        }

        document = DocumentFactory.load_from_json(json_data)

        assert document.info.url == "https://empty.com"
        assert len(document.root.children) == 0
        assert len(document.elements) == 1

    def test_load_from_json_missing_url(self):
        json_data = {
            "root_elements": [
                {
                    "tag": "div",
                    "text": "Content",
                    "alt": None,
                    "title": None,
                    "placeholder": None,
                    "width": "auto",
                    "height": "auto",
                    "top": "0px",
                    "left": "0px",
                    "fontSize": "16px",
                    "fontWeight": "400",
                    "lineHeight": "normal",
                    "opacity": "1",
                    "letterSpacing": "normal",
                    "color": "rgb(0, 0, 0)",
                    "backgroundColor": "rgb(255, 255, 255)",
                    "position": "static",
                    "display": "block",
                    "textAlign": "left",
                    "depth": 0,
                    "num_children": 0
                }
            ]
        }

        document = DocumentFactory.load_from_json(json_data)

        assert document.info.title == "Analyzed Document"
        assert len(document.root.children) == 1


class TestDocumentModel:
    def test_document_model_creation(self):
        info = DocumentInfo(title="Test Document", lang="en")
        root = ElementNode(tag="html", text="Content")
        elements = [root]

        model = DocumentModel(info=info, root=root, elements=elements)

        assert model.info.title == "Test Document"
        assert model.root.tag == "html"
        assert len(model.elements) == 1


def test_full_feature_example():
    full_feature_json = {
        "root_elements": [
            {
                "tag": "h1",
                "text": "Главный заголовок страницы",
                "alt": None,
                "title": "Заголовок первого уровня",
                "computedStyles": {
                    "fontSize": "32px",
                    "fontWeight": "700",
                    "lineHeight": "1.2",
                    "opacity": "1",
                    "letterSpacing": "normal",
                    "color": "rgb(33, 37, 41)",
                    "backgroundColor": "rgb(255, 255, 255)",
                    "position": "static",
                    "display": "block",
                    "textAlign": "left",
                },
                "attributes": {
                    "placeholder": None,
                    "width": "720px",
                    "height": "48px",
                    "top": "20px",
                    "left": "50px"
                },
                "depth": 2,
                "num_children": 0
            },
            {
                "tag": "button",
                "text": "Нажми меня",
                "alt": None,
                "title": "Кнопка для отправки формы",
                "computedStyles": {
                    "fontSize": "16px",
                    "fontWeight": "500",
                    "lineHeight": "1.5",
                    "opacity": "0.95",
                    "letterSpacing": "0.5px",
                    "color": "rgb(255, 255, 255)",
                    "backgroundColor": "rgb(0, 123, 255)",
                    "position": "relative",
                    "display": "inline-block",
                    "textAlign": "center"
                },
                "attributes": {
                    "placeholder": None,
                    "width": "120px",
                    "height": "40px",
                    "top": "80px",
                    "left": "50px"
                },
                "depth": 3,
                "num_children": 1
            },
            {
                "tag": "input",
                "text": "",
                "alt": "Поле для ввода email",
                "title": "Введите ваш адрес электронной почты",
                "computedStyles": {
                    "fontSize": "16px",
                    "fontWeight": "400",
                    "lineHeight": "normal",
                    "opacity": "1",
                    "letterSpacing": "normal",
                    "color": "rgb(73, 80, 87)",
                    "backgroundColor": "rgb(255, 255, 255)",
                    "position": "static",
                    "display": "block",
                    "textAlign": "start"
                },
                "attributes": {
                    "placeholder": "user@example.com",
                    "width": "300px",
                    "height": "38px",
                    "top": "140px",
                    "left": "auto"
                },
                "depth": 3,
                "num_children": 0
            }
        ]
    }

    document = DocumentFactory.load_from_json(full_feature_json)

    assert isinstance(document, DocumentModel)
    assert len(document.elements) == 4
    assert len(document.root.children) == 3

    h1_element = document.elements[1]
    assert h1_element.tag == "h1"
    assert h1_element.text == "Главный заголовок страницы"
    assert h1_element.alt is None
    assert h1_element.title == "Заголовок первого уровня"
    assert h1_element.placeholder is None
    assert h1_element.width == "720px"
    assert h1_element.height == "48px"
    assert h1_element.top == "20px"
    assert h1_element.left == "50px"
    assert h1_element.depth == 2
    assert h1_element.num_children == 0
    assert h1_element.fontSize == "32px"
    assert h1_element.fontWeight == "700"
    assert h1_element.lineHeight == "1.2"
    assert h1_element.opacity == "1"
    assert h1_element.letterSpacing == "normal"
    assert h1_element.color == "rgb(33, 37, 41)"
    assert h1_element.backgroundColor == "rgb(255, 255, 255)"
    assert h1_element.position == "static"
    assert h1_element.display == "block"
    assert h1_element.textAlign == "left"

    button_element = document.elements[2]
    assert button_element.tag == "button"
    assert button_element.text == "Нажми меня"
    assert button_element.alt is None
    assert button_element.title == "Кнопка для отправки формы"
    assert button_element.placeholder is None
    assert button_element.width == "120px"
    assert button_element.height == "40px"
    assert button_element.top == "80px"
    assert button_element.left == "50px"
    assert button_element.depth == 3
    assert button_element.num_children == 0
    assert button_element.fontSize == "16px"
    assert button_element.fontWeight == "500"
    assert button_element.lineHeight == "1.5"
    assert button_element.opacity == "0.95"
    assert button_element.letterSpacing == "0.5px"
    assert button_element.color == "rgb(255, 255, 255)"
    assert button_element.backgroundColor == "rgb(0, 123, 255)"
    assert button_element.position == "relative"
    assert button_element.display == "inline-block"
    assert button_element.textAlign == "center"

    input_element = document.elements[3]
    assert input_element.tag == "input"
    assert input_element.text == ""
    assert input_element.alt == "Поле для ввода email"
    assert input_element.title == "Введите ваш адрес электронной почты"
    assert input_element.placeholder == "user@example.com"
    assert input_element.width == "300px"
    assert input_element.height == "38px"
    assert input_element.top == "140px"
    assert input_element.left == "auto"
    assert input_element.depth == 3
    assert input_element.num_children == 0
    assert input_element.fontSize == "16px"
    assert input_element.fontWeight == "400"
    assert input_element.lineHeight == "normal"
    assert input_element.opacity == "1"
    assert input_element.letterSpacing == "normal"
    assert input_element.color == "rgb(73, 80, 87)"
    assert input_element.backgroundColor == "rgb(255, 255, 255)"
    assert input_element.position == "static"
    assert input_element.display == "block"
    assert input_element.textAlign == "start"

# test_parse_and_write_dto.py
import json
from pathlib import Path

# Путь к файлу с "сырыми" данными элементов (представим, что это массив JSON-объектов)
INPUT_FILE_PATH = "testspack/test_parser/test_output/hack_bank_data.json"
OUTPUT_FILE_PATH = "testspack/test_parser/test_output/dto_output.txt"


def test_parse_json_file_and_write_dto():
    """
    Тест: читает JSON, преобразует в DocumentModel через DocumentFactory,
    разворачивает DOM в плоский список и записывает детали в файл.
    """

    input_path = Path(INPUT_FILE_PATH)
    output_path = Path(OUTPUT_FILE_PATH)

    # --- 1. Читаем содержимое JSON ---
    assert input_path.exists(), f"Файл {input_path} не найден"

    json_string = input_path.read_text(encoding="utf-8")

    try:
        parsed_data = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Ошибка при чтении JSON: {e}")

    # --- 2. Преобразуем в DocumentModel ---
    document_model = DocumentFactory.load_from_json(parsed_data)

    # --- 3. Записываем данные о модели ---
    with output_path.open("w", encoding="utf-8") as f:
        f.write("DOCUMENT MODEL DTO DUMP\n")
        f.write("=" * 60 + "\n\n")

        # Информация о документе
        f.write("Document Info:\n")
        f.write(f"Title: {document_model.info.title}\n")
        f.write(f"Lang: {document_model.info.lang}\n")
        f.write(f"Parse errors: {document_model.info.parse_errors}\n")
        f.write("\n")

        # Техническая статистика
        f.write("STATS:\n")
        f.write(f"Total elements (flat): {len(document_model.elements)}\n")
        f.write(f"Root children count: {len(document_model.root.children)}\n")
        f.write("\n")

        # Все элементы
        f.write("--- ALL ELEMENTS ---\n")

        for i, elem in enumerate(document_model.elements, start=1):
            f.write(f"\n### Element {i} ###\n")
            f.write(f"tag: {elem.tag}\n")
            f.write(f"text: {elem.text}\n")
            f.write(f"node_id: {elem.node_id}\n")

            # DOM путь (если есть)
            if hasattr(elem, "get_path"):
                try:
                    f.write(f"path: {elem.get_path()}\n")
                except Exception:
                    f.write("path: <error calculating path>\n")

            f.write(f"children count: {len(elem.children)}\n")
            f.write(f"parent: {elem.parent.tag if elem.parent else None}\n")

            # ПОЛНЫЕ данные узла — автоматически
            f.write("\n--- RAW NODE DATA ---\n")
            for key, value in vars(elem).items():
                f.write(f"{key}: {value}\n")

            f.write("-" * 40 + "\n")

    # --- 4. Проверяем корректность вывода ---
    assert output_path.exists(), "Выходной файл не создан"
    assert output_path.stat().st_size > 0, "Выходной файл пустой"

    print(f"DTO успешно записан → {output_path}")
    print(f"Всего элементов: {len(document_model.elements)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])