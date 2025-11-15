import pytest
from app.services.accessibility.analytics.json_parser.models import ElementNode


# ------------------------------------------------------------
# Helper – простой тестовый json
# ------------------------------------------------------------
TEST_JSON = {
    "tag": "div",
    "text": "root",
    "children": [
        {
            "tag": "h1",
            "text": "Header"
        },
        {
            "tag": "section",
            "text": "Middle",
            "children": [
                {
                    "tag": "p",
                    "text": "Paragraph"
                }
            ]
        },
        {
            "tag": "footer",
            "text": "Bottom"
        }
    ]
}


@pytest.fixture
def root_node():
    return ElementNode.from_json(TEST_JSON)


# ------------------------------------------------------------
# 1. Проверяем базовую структуру и parent link
# ------------------------------------------------------------
def test_tree_structure(root_node):
    assert root_node.tag == "div"
    assert len(root_node.children) == 3

    h1 = root_node.children[0]
    section = root_node.children[1]
    footer = root_node.children[2]

    assert h1.parent is root_node
    assert section.parent is root_node
    assert footer.parent is root_node

    assert section.children[0].parent is section


# ------------------------------------------------------------
# 2. Проверяем обход вверх (parent)
# ------------------------------------------------------------
def test_walk_up(root_node):
    paragraph = root_node.children[1].children[0]

    tags = []
    node = paragraph
    while node:
        tags.append(node.tag)
        node = node.parent

    assert tags == ["p", "section", "div"]


# ------------------------------------------------------------
# 3. Проверяем соседей (previous / next sibling)
# ------------------------------------------------------------
def test_siblings_navigation(root_node):
    h1 = root_node.children[0]
    section = root_node.children[1]
    footer = root_node.children[2]

    def get_prev(node):
        parent = node.parent
        if not parent:
            return None
        siblings = parent.children
        idx = siblings.index(node)
        return siblings[idx - 1] if idx > 0 else None

    def get_next(node):
        parent = node.parent
        if not parent:
            return None
        siblings = parent.children
        idx = siblings.index(node)
        return siblings[idx + 1] if idx < len(siblings) - 1 else None

    assert get_prev(section) is h1
    assert get_next(section) is footer
    assert get_prev(h1) is None
    assert get_next(footer) is None


# ------------------------------------------------------------
# 4. Проверяем DFS – document order
# ------------------------------------------------------------
def test_dfs_order(root_node):

    def dfs(node, result):
        result.append(node.tag)
        for c in node.children:
            dfs(c, result)
        return result

    order = dfs(root_node, [])

    assert order == ["div", "h1", "section", "p", "footer"]


# ------------------------------------------------------------
# 5. Проверяем BFS (ширина)
# ------------------------------------------------------------
def test_bfs_order(root_node):

    def bfs(start):
        queue = [start]
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node.tag)
            queue.extend(node.children)
        return order

    order = bfs(root_node)

    assert order == ["div", "h1", "section", "footer", "p"]


# ------------------------------------------------------------
# 6. Проверяем get_path() если он реализован
# ------------------------------------------------------------
def test_get_path(root_node):
    paragraph = root_node.children[1].children[0]

    path = paragraph.get_path()

    assert path == "div > section > p"
