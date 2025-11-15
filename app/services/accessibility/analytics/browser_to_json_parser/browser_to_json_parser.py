import aiohttp
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
from typing import List, Optional, Dict, Any
import json
from dataclasses import dataclass, field


# -----------------------
# Data Classes
# -----------------------

@dataclass
class ElementNode:
    tag: str
    id: Optional[str] = None
    classes: List[str] = field(default_factory=list)
    text: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    computedStyles: Dict[str, Any] = field(default_factory=dict)
    depth: int = 0
    index: int = 0
    parent_id: Optional[str] = None
    children: List['ElementNode'] = field(default_factory=list)


# -----------------------
# Helpers
# -----------------------

def css_prop_to_camel(prop: str) -> str:
    """
    Преобразует CSS ключи:
    font-weight → fontWeight
    background-color → backgroundColor
    """
    parts = prop.split("-")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def parse_inline_styles(style: str) -> dict:
    """
    Разбирает inline CSS из атрибута style=""
    Возвращает camelCase свойства.
    """
    result = {}
    if not style:
        return result

    parts = style.split(";")
    for part in parts:
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        camel = css_prop_to_camel(key.strip())
        result[camel] = value.strip()

    return result


async def fetch_html(url: str) -> str | None:
    """
    Загружает HTML c помощью aiohttp с улучшенной обработкой ошибок
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=timeout) as resp:
                if resp.status != 200:
                    print(f"HTTP Error: {resp.status} for {url}")
                    return None
                return await resp.text()
    except aiohttp.ClientError as e:
        print(f"Network error for {url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {url}: {e}")
        return None


def element_to_node(el: Tag, depth: int = 0, index: int = 0, parent_id: str = None) -> ElementNode:
    """
    Рекурсивно преобразует BeautifulSoup элемент в ElementNode с детьми
    """
    element_id = el.get('id', '')

    # Создаем узел
    node = ElementNode(
        tag=el.name,
        id=element_id,
        classes=el.get("class", []),
        text=el.get_text(strip=True)[:500],
        depth=depth,
        index=index,
        parent_id=parent_id
    )

    # Атрибуты
    for attr, value in el.attrs.items():
        if attr == "class":
            continue
        if isinstance(value, list):
            node.attributes[attr] = ' '.join(value)
        else:
            node.attributes[attr] = str(value)

    # Inline styles
    inline_css = el.get("style", "")
    node.computedStyles = parse_inline_styles(inline_css)

    # Рекурсивно обрабатываем детей
    child_index = 0
    for child in el.children:
        if isinstance(child, Tag):
            child_node = element_to_node(child, depth + 1, child_index, element_id)
            node.children.append(child_node)
            child_index += 1

    return node


def element_node_to_dict(node: ElementNode) -> Dict[str, Any]:
    """
    Рекурсивно преобразует ElementNode в словарь для JSON
    """
    return {
        "tag": node.tag,
        "id": node.id,
        "classes": node.classes,
        "text": node.text,
        "attributes": node.attributes,
        "computedStyles": node.computedStyles,
        "depth": node.depth,
        "index": node.index,
        "parent_id": node.parent_id,
        "children": [element_node_to_dict(child) for child in node.children]
    }


def filter_nodes_by_selectors(root_nodes: List[ElementNode], selectors: List[str], soup: BeautifulSoup) -> List[
    ElementNode]:
    """
    Фильтрует элементы по CSS селекторам, сохраняя структуру
    """
    if not selectors:
        return root_nodes

    # Находим все элементы по селекторам
    selected_elements = set()
    for selector in selectors:
        try:
            elements = soup.select(selector)
            selected_elements.update(elements)
        except Exception as e:
            print(f"Selector error '{selector}': {e}")
            continue

    def filter_tree(node: ElementNode, soup_elements: set) -> Optional[ElementNode]:
        # Находим соответствующий BeautifulSoup элемент
        soup_element = find_soup_element_for_node(node, soup)
        if soup_element in soup_elements:
            return node

        # Рекурсивно фильтруем детей
        filtered_children = []
        for child in node.children:
            filtered_child = filter_tree(child, soup_elements)
            if filtered_child:
                filtered_children.append(filtered_child)

        if filtered_children:
            # Создаем копию узла с отфильтрованными детьми
            node_copy = ElementNode(
                tag=node.tag,
                id=node.id,
                classes=node.classes.copy(),
                text=node.text,
                attributes=node.attributes.copy(),
                computedStyles=node.computedStyles.copy(),
                depth=node.depth,
                index=node.index,
                parent_id=node.parent_id,
                children=filtered_children
            )
            return node_copy

        return None

    # Применяем фильтрацию ко всем корневым узлам
    filtered_root = []
    for node in root_nodes:
        filtered_node = filter_tree(node, selected_elements)
        if filtered_node:
            filtered_root.append(filtered_node)

    return filtered_root


def find_soup_element_for_node(node: ElementNode, soup: BeautifulSoup) -> Optional[Tag]:
    """
    Находит BeautifulSoup элемент для ElementNode
    """
    try:
        tag = node.tag
        element_id = node.id
        classes = node.classes
        text = node.text

        # Пытаемся найти по ID
        if element_id:
            selector = f"#{element_id}"
            elements = soup.select(selector)
            if elements:
                return elements[0]

        # Пытаемся найти по комбинации тега, классов и текста
        selector_parts = [tag]
        if classes:
            for cls in classes:
                selector_parts.append(f".{cls}")

        selector = "".join(selector_parts)
        elements = soup.select(selector)

        for el in elements:
            if el.get_text(strip=True)[:500] == text:
                return el

        return None
    except Exception:
        return None


async def parse_url(url: str, selectors: list[str] | None = None) -> dict | None:
    """
    Основная функция парсера с поддержкой древовидной структуры ElementNode
    """
    try:
        html = await fetch_html(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # META SECTION
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        html_tag = soup.find("html")
        lang = html_tag.get("lang", "") if html_tag else ""
        charset = None

        meta_charset = soup.find("meta", charset=True)
        if meta_charset:
            charset = meta_charset.get("charset")

        meta_http = soup.find("meta", attrs={"http-equiv": "Content-Type"})
        if not charset and meta_http:
            content = meta_http.get("content", "")
            if "charset=" in content:
                charset = content.split("charset=")[-1]

        charset = (charset or "").upper()

        # Строим полное дерево ElementNode
        root_nodes = []

        # Обрабатываем корневые элементы
        for i, child in enumerate(soup.children):
            if isinstance(child, Tag):
                root_node = element_to_node(child, depth=0, index=i, parent_id=None)
                root_nodes.append(root_node)

        # Если указаны селекторы, фильтруем дерево
        if selectors:
            root_nodes = filter_nodes_by_selectors(root_nodes, selectors, soup)

        # Преобразуем ElementNode в словари для JSON
        root_elements_dict = [element_node_to_dict(node) for node in root_nodes]

        result = {
            "meta": {
                "url": url,
                "title": title,
                "lang": lang,
                "charset": charset,
            },
            "root_elements": root_elements_dict
        }

        return result

    except Exception as e:
        print(f"Parse URL error: {e}")
        return None


# Утилиты для работы с ElementNode
def count_nodes(node: ElementNode) -> int:
    """Считает общее количество элементов в дереве"""
    count = 1
    for child in node.children:
        count += count_nodes(child)
    return count


def find_nodes_by_tag(node: ElementNode, tag: str) -> List[ElementNode]:
    """Находит все элементы с указанным тегом"""
    results = []
    if node.tag == tag:
        results.append(node)

    for child in node.children:
        results.extend(find_nodes_by_tag(child, tag))

    return results


def print_node_structure(node: ElementNode, level: int = 0):
    """Печатает структуру дерева ElementNode"""
    indent = "  " * level
    tag = node.tag
    element_id = f"#{node.id}" if node.id else ""
    classes = "." + ".".join(node.classes) if node.classes else ""
    text_preview = node.text[:30] + "..." if node.text and len(node.text) > 30 else node.text

    print(f"{indent}{tag}{element_id}{classes}: {text_preview}")

    for child in node.children:
        print_node_structure(child, level + 1)


# Функция для загрузки из JSON обратно в ElementNode
def dict_to_element_node(data: Dict[str, Any]) -> ElementNode:
    """Преобразует словарь обратно в ElementNode"""
    node = ElementNode(
        tag=data["tag"],
        id=data["id"],
        classes=data["classes"],
        text=data["text"],
        attributes=data["attributes"],
        computedStyles=data["computedStyles"],
        depth=data["depth"],
        index=data["index"],
        parent_id=data["parent_id"]
    )

    # Рекурсивно обрабатываем детей
    for child_data in data.get("children", []):
        child_node = dict_to_element_node(child_data)
        node.children.append(child_node)

    return node


# Пример использования
async def main():
    url = "https://www.yahoo.com/"
    selectors = ["header", "main", "footer", "a", "button"]  # опционально

    result = await parse_url(url, selectors)

    if result:
        # Сохраняем в файл
        with open("dom_tree.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        # Загружаем обратно в ElementNode для работы
        root_nodes = [dict_to_element_node(root_data) for root_data in result["root_elements"]]

        # Печатаем структуру
        for root_node in root_nodes:
            print_node_structure(root_node)

        total_elements = sum(count_nodes(node) for node in root_nodes)
        print(f"\nTotal elements: {total_elements}")

        # Пример поиска
        all_links = []
        for root_node in root_nodes:
            all_links.extend(find_nodes_by_tag(root_node, "a"))

        print(f"Found {len(all_links)} links")

