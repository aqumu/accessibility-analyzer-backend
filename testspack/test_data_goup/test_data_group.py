import pytest
from  app.services.analytics.json_parser.models import (
    DocumentInfo,
    DocumentModel,
    DocumentFactory,
    ElementNode,
    NodeSemantics,
    NodeInteraction
)
from app.services.analytics.data_group.data_group import (
    DataGroupExtractor,
    ImageData,
    FormFieldData,
    InteractiveData,
    StyleData,
    MediaData,
    HeadingData,
    TableData,
    AriaData,
    DocumentStructureData
)


class TestImageData:

    def test_image_data_extraction_basic(self):
        node = ElementNode(
            tag="img",
            node_id="img1",
            alt="A cat",
            title="Fluffy Cat",
            attributes={"src": "cat.jpg", "id": "cat_img"}
        )
        img_data = ImageData(node)

        assert img_data.node_id == "img1"
        assert img_data.tag == "img"
        assert img_data.alt == "A cat"
        assert img_data.title == "Fluffy Cat"
        assert img_data.src == "cat.jpg"
        assert img_data.attributes == {"src": "cat.jpg", "id": "cat_img"}
        assert img_data.is_content_image is True

    def test_image_data_no_alt_title(self):
        node = ElementNode(
            tag="img",
            node_id="img2",
            alt=None,
            title=None,
            attributes={"src": "dog.jpg"}
        )
        img_data = ImageData(node)

        assert img_data.alt is None
        assert img_data.title is None
        assert img_data.src == "dog.jpg"
        assert img_data.is_content_image is False

    def test_image_data_empty_alt(self):
        node = ElementNode(
            tag="img",
            node_id="img3",
            alt="",
            title=None,
            attributes={"src": "bird.jpg"}
        )
        img_data = ImageData(node)

        assert img_data.alt == ""
        assert img_data.src == "bird.jpg"
        assert img_data.is_content_image is False

    def test_image_data_only_title(self):
        node = ElementNode(
            tag="img",
            node_id="img4",
            alt="",
            title="A picture",
            attributes={"src": "pic.jpg"}
        )
        img_data = ImageData(node)

        assert img_data.alt == ""
        assert img_data.title == "A picture"
        assert img_data.src == "pic.jpg"
        assert img_data.is_content_image is True

    def test_image_data_no_src(self):
        node = ElementNode(
            tag="img",
            node_id="img5",
            alt="No src image",
            title=None,
            attributes={"id": "no_src_img"}
        )
        img_data = ImageData(node)

        assert img_data.alt == "No src image"
        assert img_data.src is None
        assert img_data.is_content_image is True


class TestFormFieldData:

    def test_form_field_data_extraction_basic(self):
        node = ElementNode(
            tag="input",
            node_id="input1",
            placeholder="Enter name",
            text="",
            attributes={"id": "name_field", "type": "text"},
            semantics=NodeSemantics(aria_label="Name Input")
        )
        field_data = FormFieldData(node)

        assert field_data.node_id == "input1"
        assert field_data.tag == "input"
        assert field_data.placeholder == "Enter name"
        assert field_data.aria_label == "Name Input"
        assert field_data.has_explicit_label is False

    def test_form_field_data_no_placeholder_or_aria(self):
        node = ElementNode(
            tag="textarea",
            node_id="textarea1",
            placeholder=None,
            text="",
            attributes={"id": "desc_field"},
            semantics=NodeSemantics(aria_label=None)
        )
        field_data = FormFieldData(node)

        assert field_data.placeholder is None
        assert field_data.aria_label is None


class TestInteractiveData:

    def test_interactive_data_extraction_button(self):
        node = ElementNode(
            tag="button",
            node_id="btn1",
            text="Submit",
            attributes={"tabindex": "0"},
            semantics=NodeSemantics(aria_label="Submit form"),
            interaction=NodeInteraction(tabindex=0)
        )
        inter_data = InteractiveData(node)

        assert inter_data.node_id == "btn1"
        assert inter_data.tag == "button"
        assert inter_data.text == "Submit"
        assert inter_data.tabindex == 0
        assert inter_data.aria_label == "Submit form"
        assert inter_data.is_empty_link is False

    def test_interactive_data_extraction_button_no_interaction(self):
        node = ElementNode(
            tag="button",
            node_id="btn2",
            text="Submit2",
            attributes={"tabindex": "1"},  # tabindex в attributes
            semantics=NodeSemantics(aria_label="Submit form 2"),
            interaction=None  # Нет interaction
        )
        inter_data = InteractiveData(node)

        assert inter_data.node_id == "btn2"
        assert inter_data.tabindex == "1"

    def test_interactive_data_extraction_empty_link(self):
        node = ElementNode(
            tag="a",
            node_id="link1",
            text="",
            attributes={"href": "#"}
        )
        inter_data = InteractiveData(node)

        assert inter_data.is_empty_link is True

    def test_interactive_data_extraction_non_empty_link(self):
        node = ElementNode(
            tag="a",
            node_id="link2",
            text="Click here",
            attributes={"href": "/page"}
        )
        inter_data = InteractiveData(node)

        assert inter_data.is_empty_link is False
        assert inter_data.text == "Click here"


class TestStyleData:

    def test_style_data_extraction(self):
        node = ElementNode(
            tag="div",
            node_id="div1",
            text="Sample text",
            color="rgb(0, 0, 0)",
            backgroundColor="rgb(255, 255, 255)",
            fontSize="16px",
            styles={"outline": "none"},
            computed={"color": "rgb(0, 0, 0)"}
        )
        style_data = StyleData(node)

        assert style_data.node_id == "div1"
        assert style_data.text == "Sample text"
        assert style_data.color == "rgb(0, 0, 0)"
        assert style_data.backgroundColor == "rgb(255, 255, 255)"
        assert style_data.fontSize == "16px"
        assert style_data.styles.get("outline") == "none"


class TestMediaData:

    def test_media_data_extraction_video(self):
        node = ElementNode(
            tag="video",
            node_id="vid1",
            attributes={"src": "video.mp4", "autoplay": True, "muted": False}
        )
        media_data = MediaData(node)

        assert media_data.node_id == "vid1"
        assert media_data.tag == "video"
        assert media_data.src == "video.mp4"
        assert media_data.autoplay is True
        assert media_data.muted is False

    def test_media_data_extraction_iframe(self):
        node = ElementNode(
            tag="iframe",
            node_id="iframe1",
            title="Embedded Content",
            attributes={"src": "https://example.com"}
        )
        media_data = MediaData(node)

        assert media_data.node_id == "iframe1"
        assert media_data.tag == "iframe"
        assert media_data.title == "Embedded Content"
        assert media_data.src == "https://example.com"
        assert media_data.autoplay is None


class TestHeadingData:

    def test_heading_data_extraction(self):
        node = ElementNode(
            tag="h1",
            node_id="h1_1",
            text="Main Title",
            attributes={"id": "main-title"}
        )
        heading_data = HeadingData(node)

        assert heading_data.node_id == "h1_1"
        assert heading_data.tag == "h1"
        assert heading_data.text == "Main Title"


class TestTableData:

    def test_table_data_extraction(self):
        child_th = ElementNode(tag="th", text="Header 1")
        node = ElementNode(
            tag="table",
            node_id="table1",
            attributes={"id": "my-table"},
            children=[child_th]
        )
        table_data = TableData(node)

        assert table_data.node_id == "table1"
        assert table_data.tag == "table"
        assert len(table_data.children) == 1
        assert table_data.children[0].tag == "th"


class TestAriaData:

    def test_aria_data_extraction_with_semantics(self):
        node = ElementNode(
            tag="div",
            node_id="div_aria1",
            attributes={"aria-hidden": "true", "aria-describedby": "desc1"},
            semantics=NodeSemantics(role="button", aria_hidden=True)
        )
        aria_data = AriaData(node)

        assert aria_data.node_id == "div_aria1"
        assert aria_data.role == "button"
        assert aria_data.aria_hidden is True
        assert "aria-hidden" in aria_data.raw_aria_attrs
        assert "aria-describedby" in aria_data.raw_aria_attrs

    def test_aria_data_extraction_no_aria_attrs(self):
        node = ElementNode(
            tag="span",
            node_id="span1",
            attributes={"class": "highlight"},
            semantics=NodeSemantics(role=None)
        )
        aria_data = AriaData(node)

        assert aria_data.role is None
        assert aria_data.aria_hidden is False
        assert aria_data.raw_aria_attrs == {}


class TestDocumentStructureData:

    def test_document_structure_data_extraction(self):
        doc_info = DocumentInfo(url="https://example.com", title="Test Page", lang="en")
        root = ElementNode(tag="html", text="Root")
        elements = [root, ElementNode(tag="body", text="Body")]
        doc_model = DocumentModel(info=doc_info, root=root, elements=elements)

        struct_data = DocumentStructureData(doc_model)

        assert struct_data.url == "https://example.com"
        assert struct_data.title == "Test Page"
        assert struct_data.lang == "en"
        assert struct_data.elements == elements
        assert struct_data.root == root


class TestDataGroupExtractor:

    def test_extract_image_data(self):
        doc_model = self._create_sample_doc_model()
        images = DataGroupExtractor.extract_image_data(doc_model)

        assert len(images) == 2
        assert all(isinstance(img, ImageData) for img in images)
        tags = [img.tag for img in images]
        assert tags.count("img") == 2
        img_with_alt = next((img for img in images if img.alt == "Test image"), None)
        assert img_with_alt is not None
        assert img_with_alt.src == "test.jpg"

    def test_extract_form_field_data(self):
        doc_model = self._create_sample_doc_model()
        fields = DataGroupExtractor.extract_form_field_data(doc_model)

        assert len(fields) == 2  # input и textarea
        assert all(isinstance(f, FormFieldData) for f in fields)
        tags = [f.tag for f in fields]
        assert "input" in tags
        assert "textarea" in tags

    def test_extract_interactive_data(self):
        doc_model = self._create_sample_doc_model()
        interactive = DataGroupExtractor.extract_interactive_data(doc_model)

        assert len(interactive) == 7
        assert all(isinstance(i, InteractiveData) for i in interactive)
        tags = [i.tag for i in interactive]
        assert tags.count("button") == 2 # button и button2
        assert "a" in tags
        assert "input" in tags
        assert "area" in tags
        assert "summary" in tags

    def test_extract_style_data(self):
        doc_model = self._create_sample_doc_model()
        styles = DataGroupExtractor.extract_style_data(doc_model)

        assert len(styles) == 6
        assert all(isinstance(s, StyleData) for s in styles)

    def test_extract_media_data(self):
        doc_model = self._create_sample_doc_model()
        media = DataGroupExtractor.extract_media_data(doc_model)

        assert len(media) == 2  # video, iframe
        assert all(isinstance(m, MediaData) for m in media)
        tags = [m.tag for m in media]
        assert "video" in tags
        assert "iframe" in tags

    def test_extract_heading_data(self):
        doc_model = self._create_sample_doc_model()
        headings = DataGroupExtractor.extract_heading_data(doc_model)

        assert len(headings) == 1
        assert isinstance(headings[0], HeadingData)
        assert headings[0].tag == "h1"
        assert headings[0].text == "Main Title"

    def test_extract_table_data(self):
        doc_model = self._create_sample_doc_model()
        tables = DataGroupExtractor.extract_table_data(doc_model)

        assert len(tables) == 1
        assert all(isinstance(t, TableData) for t in tables)
        tags = [t.tag for t in tables]
        assert "table" in tags

    def test_extract_aria_data(self):
        doc_model = self._create_sample_doc_model()
        aria_data = DataGroupExtractor.extract_aria_data(doc_model)

        assert len(aria_data) == 2
        assert all(isinstance(a, AriaData) for a in aria_data)

        role_elem = next((a for a in aria_data if a.role == "button"), None)
        assert role_elem is not None
        assert role_elem.tag == "div"

        raw_attr_elem = next((a for a in aria_data if "aria-label" in a.raw_aria_attrs), None)
        assert raw_attr_elem is not None
        assert raw_attr_elem.tag == "span"

    def test_extract_document_structure_data(self):
        doc_model = self._create_sample_doc_model()
        struct_data = DataGroupExtractor.extract_document_structure_data(doc_model)

        assert isinstance(struct_data, DocumentStructureData)
        assert struct_data.url == doc_model.info.url
        assert struct_data.lang == doc_model.info.lang
        assert struct_data.elements == doc_model.elements
        assert struct_data.root == doc_model.root

    def _create_sample_doc_model(self) -> DocumentModel:
        doc_info = DocumentInfo(url="https://test.com", title="Test Doc", lang="en")

        img_elem = ElementNode(tag="img", node_id="img1", alt="Test image", attributes={"src": "test.jpg"})
        img_elem_no_alt = ElementNode(tag="img", node_id="img2", alt=None, attributes={"src": "test2.jpg"})
        input_elem = ElementNode(tag="input", node_id="input1", placeholder="Enter value")
        textarea_elem = ElementNode(tag="textarea", node_id="textarea1", text="")
        button_elem = ElementNode(tag="button", node_id="btn1", text="Click", color="blue", backgroundColor="gray",
                                  interaction=NodeInteraction(tabindex=0))
        link_elem = ElementNode(tag="a", node_id="link1", text="Link", attributes={"href": "/page"})
        div_with_styles = ElementNode(tag="div", node_id="div1", text="Styled div", color="red",
                                      backgroundColor="white")
        video_elem = ElementNode(tag="video", node_id="vid1", attributes={"src": "video.mp4", "autoplay": True})
        iframe_elem = ElementNode(tag="iframe", node_id="iframe1", title="Frame",
                                  attributes={"src": "https://iframe.com"})
        h1_elem = ElementNode(tag="h1", node_id="h1_1", text="Main Title")
        table_elem = ElementNode(tag="table", node_id="table1", children=[
            ElementNode(tag="th", node_id="th1", text="Header")
        ])
        area_elem = ElementNode(tag="area", node_id="area1", attributes={"shape": "rect", "coords": "0,0,100,100"})
        div_with_role = ElementNode(tag="div", node_id="div_role1", semantics=NodeSemantics(role="button"))
        span_with_aria = ElementNode(tag="span", node_id="span_aria1", attributes={"aria-label": "A label"})
        button_elem2 = ElementNode(tag="button", node_id="btn2", text="Click2", attributes={"tabindex": "1"},
                                   interaction=None)
        summary_elem = ElementNode(tag="summary", node_id="summary1", text="Details summary")

        elements = [
            img_elem, img_elem_no_alt, input_elem, textarea_elem, button_elem, link_elem,
            div_with_styles, video_elem, iframe_elem, h1_elem, table_elem,
            area_elem, div_with_role, span_with_aria, button_elem2, summary_elem
        ]

        root = ElementNode(tag="html", children=elements)
        return DocumentModel(info=doc_info, root=root, elements=elements)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])