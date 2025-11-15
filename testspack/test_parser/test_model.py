# test_model.py
import pytest
from app.services.accessibility.analytics.json_parser.models import (
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
        info = DocumentInfo(title="Test Page", lang="en")
        assert info.title == "Test Page"
        assert info.lang == "en"
        assert info.parse_errors == []

    def test_document_info_with_errors(self):
        errors = ["Error 1", "Error 2"]
        info = DocumentInfo(title="Test Page", lang="ru", parse_errors=errors)
        assert info.parse_errors == errors

    def test_document_info_defaults(self):
        info = DocumentInfo(title="Test Page")
        assert info.lang == "en"
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
        }

        node = ElementNode.from_json(json_data)

        assert node.tag == "h1"
        assert node.text == "Main Title"
        assert node.title == "Main Title"

        assert node.fontSize == "32px"
        assert node.fontWeight == "700"
        assert node.color == "rgb(33, 37, 41)"
        assert node.backgroundColor == "rgb(255, 255, 255)"
        assert node.width == "720px"
        assert node.height == "48px"
        assert node.depth == 2
        assert node.num_children == 0

        assert "color" in node.styles
        assert node.styles["color"] == "rgb(33, 37, 41)"
        assert node.styles["fontSize"] == "32px"

    def test_element_node_from_json_with_media(self):
        json_data = {
            "tag": "img",
            "text": "",
            "alt": "Description of image",
            "title": "Image title",
            "placeholder": None,
            "width": "300px",
            "height": "200px",
            "top": "100px",
            "left": "50px",
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
            "depth": 1,
            "num_children": 0
        }

        node = ElementNode.from_json(json_data)

        assert node.media is not None
        assert node.media.alt == "Description of image"
        assert node.media.title == "Image title"

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
                "aria_hidden": False
            }
        }

        node = ElementNode.from_json(json_data)

        assert node.semantics is not None
        assert node.semantics.role == "button"
        assert node.semantics.aria_label == "Submit form"

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
                    "depth": 1,
                    "num_children": 0
                }
            ]
        }

        node = ElementNode.from_json(json_data)

        assert len(node.children) == 1
        assert node.children[0].tag == "span"
        assert node.children[0].text == "Child"


class TestDocumentFactory:
    def test_load_from_json(self):
        json_data = {
            "url": "https://example.com",
            "elements": [
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
        assert document.info.title == "https://example.com"

        assert len(document.root.children) == 2
        assert document.root.children[0].tag == "h1"
        assert document.root.children[1].tag == "button"

        assert len(document.elements) == 2
        assert document.elements[0].text == "Main Title"
        assert document.elements[1].text == "Click me"

    def test_load_from_json_empty_elements(self):
        json_data = {
            "url": "https://empty.com",
            "elements": []
        }

        document = DocumentFactory.load_from_json(json_data)

        assert document.info.title == "https://empty.com"
        assert len(document.root.children) == 0
        assert len(document.elements) == 0

    def test_load_from_json_missing_url(self):
        json_data = {
            "elements": [
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
        "elements": [
            {
                "tag": "h1",
                "text": "Главный заголовок страницы",
                "alt": None,
                "title": "Заголовок первого уровня",
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
                "text": "Нажми меня",
                "alt": None,
                "title": "Кнопка для отправки формы",
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
            },
            {
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
                "num_children": 0
            }
        ]
    }

    document = DocumentFactory.load_from_json(full_feature_json)

    assert isinstance(document, DocumentModel)
    assert len(document.elements) == 3
    assert len(document.root.children) == 3

    h1_element = document.elements[0]
    assert h1_element.tag == "h1"
    assert h1_element.text == "Главный заголовок страницы"
    assert h1_element.title == "Заголовок первого уровня"
    assert h1_element.fontSize == "32px"
    assert h1_element.color == "rgb(33, 37, 41)"
    assert h1_element.depth == 2
    assert h1_element.num_children == 0

    button_element = document.elements[1]
    assert button_element.tag == "button"
    assert button_element.text == "Нажми меня"
    assert button_element.title == "Кнопка для отправки формы"
    assert button_element.backgroundColor == "rgb(0, 123, 255)"
    assert button_element.depth == 3
    assert button_element.num_children == 1

    input_element = document.elements[2]
    assert input_element.tag == "input"
    assert input_element.text == ""
    assert input_element.alt == "Поле для ввода email"
    assert input_element.placeholder == "user@example.com"
    assert input_element.fontSize == "16px"
    assert input_element.depth == 3
    assert input_element.num_children == 0


if __name__ == "__main__":
    pytest.main([__file__])