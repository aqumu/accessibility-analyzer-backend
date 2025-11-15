import pytest
import json
from pathlib import Path
from app.services.accessibility.analytics.json_parser.models import DocumentFactory, DocumentModel, ElementNode, MediaInfo  # замените на реальный путь

# ---------------------------
# Пример JSON для теста
# ---------------------------
example_json = {
    "document": {
        "title": "Example Page",
        "lang": "en",
        "parse_errors": []
    },
    "dom": {
        "tag": "html",
        "children": [
            {
                "tag": "head",
                "children": [
                    {"tag": "title", "text": "Example Page"}
                ]
            },
            {
                "tag": "body",
                "children": [
                    {
                        "tag": "div",
                        "attributes": {"id": "main", "class": "container"},
                        "children": [
                            {"tag": "h1", "text": "Welcome"},
                            {
                                "tag": "img",
                                "attributes": {"src": "cat.png", "alt": "A cute cat", "title": "Cat"}
                            },
                            {"tag": "p", "text": "This is an example paragraph."}
                        ]
                    }
                ]
            }
        ]
    }
}

# ---------------------------
# Тест загрузки JSON в модель
# ---------------------------
def test_load_document_model():
    doc_model: DocumentModel = DocumentFactory.load_from_json(example_json)

    # Проверяем DocumentInfo
    assert doc_model.info.title == "Example Page"
    assert doc_model.info.lang == "en"
    assert doc_model.info.parse_errors == []

    # Проверяем корневой элемент
    root: ElementNode = doc_model.root
    assert root.tag == "html"
    assert isinstance(root.children, list)
    assert len(root.children) == 2  # head + body

    # Проверяем head
    head = root.children[0]
    assert head.tag == "head"
    assert head.children[0].tag == "title"
    assert head.children[0].text == "Example Page"

    # Проверяем body и div
    body = root.children[1]
    assert body.tag == "body"
    div = body.children[0]
    assert div.tag == "div"
    assert div.attributes["id"] == "main"
    assert div.attributes["class"] == "container"

    # Проверяем h1
    h1 = div.children[0]
    assert h1.tag == "h1"
    assert h1.text == "Welcome"

    # Проверяем img и media info
    img = div.children[1]
    assert img.tag == "img"
    assert isinstance(img.media, MediaInfo)
    assert img.media.src == "cat.png"
    assert img.media.alt == "A cute cat"
    assert img.media.title == "Cat"

    # Проверяем p
    p = div.children[2]
    assert p.tag == "p"
    assert p.text == "This is an example paragraph."

# ---------------------------
# Дополнительно: проверка рекурсивного from_json для пустых children
# ---------------------------
def test_element_node_from_json_empty_children():
    node_data = {"tag": "span"}
    node = ElementNode.from_json(node_data)
    assert node.tag == "span"
    assert node.children == []
    assert node.attributes == {}
    assert node.styles == {}

EXAMPLE_JSON_FILE = Path("example_dom.json")

@pytest.mark.asyncio
def test_load_example_dom_json():
    # Проверяем, что файл существует
    assert EXAMPLE_JSON_FILE.exists(), f"{EXAMPLE_JSON_FILE} не найден. Выполните test_dump_real_dom_json сначала."

    # Загружаем JSON
    with EXAMPLE_JSON_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Парсим в модель
    doc_model: DocumentModel = DocumentFactory.load_from_json(data)

    # ---------------------------
    # Проверяем основные поля документа
    # ---------------------------
    assert isinstance(doc_model.info.title, str)
    assert isinstance(doc_model.info.lang, str)
    assert isinstance(doc_model.info.parse_errors, list)

    # ---------------------------
    # Проверяем корневой узел
    # ---------------------------
    root: ElementNode = doc_model.root
    assert isinstance(root.tag, str)
    assert isinstance(root.children, list)

    # Пробежим рекурсивно по всем элементам, чтобы проверить хотя бы tag и children
    def check_node(node: ElementNode):
        assert isinstance(node.tag, str)
        assert isinstance(node.children, list)
        for child in node.children:
            check_node(child)

        # Если это img, проверяем media
        if node.tag == "img":
            assert isinstance(node.media, MediaInfo)
            assert node.media.src is not None

    check_node(root)

    print("[OK] example_dom.json успешно загружен в модель DocumentModel")