import aiohttp
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import cssutils
from cssselect import GenericTranslator
from lxml import html, etree
import json

# ============================================================
# DATA CLASSES
# ============================================================

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
    children: List["ElementNode"] = field(default_factory=list)


# ============================================================
# HELPERS
# ============================================================

def css_prop_to_camel(prop: str) -> str:
    parts = prop.split("-")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def parse_inline_styles(style: str) -> dict:
    result = {}
    if not style:
        return result
    for part in style.split(";"):
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        result[css_prop_to_camel(k.strip())] = v.strip()
    return result


async def fetch_html(url: str) -> Optional[str]:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=timeout) as resp:
                if resp.status != 200:
                    return None
                return await resp.text()
    except:
        return None


async def fetch_css(url: str) -> Optional[str]:
    return await fetch_html(url)


# ============================================================
# CSS PARSER — FULL CASCADE
# ============================================================

@dataclass
class CSSRule:
    selector: str
    declarations: Dict[str, Any]
    specificity: tuple
    important: Dict[str, Any]
    order: int


def compute_specificity(selector: str) -> tuple:
    # A realistic specificity calculator
    # counts ID = 100, class = 10, tag = 1
    id_count = selector.count("#")
    class_count = selector.count(".")
    tag_count = sum(1 for p in selector.split() if p.isalnum())
    return (id_count, class_count, tag_count)


async def load_all_css(doc, base_url: str) -> List[str]:
    css_blocks = []

    # <style>
    for style_el in doc.xpath("//style"):
        text = style_el.text or ""
        css_blocks.append(text)

    # <link rel=stylesheet>
    for link in doc.xpath("//link[@rel='stylesheet']"):
        href = link.get("href")
        if href:
            css_url = urljoin(base_url, href)
            css = await fetch_css(css_url)
            if css:
                css_blocks.append(css)

    return css_blocks


def parse_css(css_blocks: List[str]) -> List[CSSRule]:
    rules = []
    order = 0

    for block in css_blocks:
        sheet = cssutils.parseString(block)
        for r in sheet:
            if r.type != r.STYLE_RULE:
                continue

            selector = r.selectorText
            declarations = {}
            important = {}

            for prop in r.style:
                camel = css_prop_to_camel(prop.name)
                if prop.priority == "important":
                    important[camel] = prop.value
                else:
                    declarations[camel] = prop.value

            spec = compute_specificity(selector)
            rules.append(CSSRule(
                selector=selector,
                declarations=declarations,
                important=important,
                specificity=spec,
                order=order
            ))
            order += 1

    return rules


# ============================================================
# APPLY CSS TO DOM
# ============================================================

def apply_css_to_dom(doc, rules: List[CSSRule]):
    translator = GenericTranslator()

    # Pre-cache XPath for selectors
    selector_cache = {}

    # node → style dict
    node_style_map: Dict[etree.ElementBase, Dict[str, Any]] = {}

    for rule in rules:
        selector = rule.selector
        if selector not in selector_cache:
            try:
                selector_cache[selector] = translator.css_to_xpath(selector)
            except:
                continue

        xp = selector_cache[selector]
        try:
            matches = doc.xpath(xp)
        except:
            continue

        for el in matches:
            if el not in node_style_map:
                node_style_map[el] = {}

            # normal declarations
            for k, v in rule.declarations.items():
                existing = node_style_map[el].get(k)
                if existing:
                    # compare specificity & order
                    if rule.specificity < existing["spec"]:
                        continue
                    if rule.specificity == existing["spec"] and rule.order < existing["order"]:
                        continue
                node_style_map[el][k] = {
                    "value": v,
                    "spec": rule.specificity,
                    "order": rule.order,
                    "important": False
                }

            # important declarations always override
            for k, v in rule.important.items():
                node_style_map[el][k] = {
                    "value": v,
                    "spec": (999, 999, 999),
                    "order": rule.order,
                    "important": True
                }

    # Inline style (highest priority)
    for el in doc.iter():
        inline = el.get("style")
        if not inline:
            continue
        parsed = parse_inline_styles(inline)
        if el not in node_style_map:
            node_style_map[el] = {}

        for k, v in parsed.items():
            node_style_map[el][k] = {
                "value": v,
                "spec": (9999, 9999, 9999),
                "order": 9999,
                "important": True
            }

    # Produce final style dicts
    final_styles = {}
    for el, styles in node_style_map.items():
        final_styles[el] = {k: v["value"] for k, v in styles.items()}

    return final_styles


# ============================================================
# DOM → ElementNode
# ============================================================

def build_tree(el, computed, depth=0, index=0, parent_id=None) -> ElementNode:
    tag = el.tag if isinstance(el.tag, str) else ""

    node = ElementNode(
        tag=tag,
        id=el.get("id"),
        classes=el.get("class", "").split() if el.get("class") else [],
        text=("".join(el.itertext()) or "").strip()[:500],
        attributes={k: v for k, v in el.attrib.items() if k not in ("id", "class", "style")},
        computedStyles=computed.get(el, {}),
        depth=depth,
        index=index,
        parent_id=parent_id
    )

    children = list(el)
    for i, child in enumerate(children):
        # Only element nodes
        if isinstance(child.tag, str):
            child_node = build_tree(
                child,
                computed,
                depth + 1,
                i,
                node.id
            )
            node.children.append(child_node)

    return node


def node_to_dict(node: ElementNode):
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
        "children": [node_to_dict(ch) for ch in node.children]
    }


# ============================================================
# MAIN PARSER
# ============================================================

async def parse_url(url: str):
    html_text = await fetch_html(url)
    if not html_text:
        return None

    doc = html.fromstring(html_text)

    # META
    title_el = doc.xpath("//title")
    title = title_el[0].text.strip() if title_el else ""

    html_el = doc.xpath("//html")
    lang = html_el[0].get("lang", "") if html_el else ""

    charset = ""
    meta_charset = doc.xpath("//meta[@charset]")
    if meta_charset:
        charset = meta_charset[0].get("charset", "").upper()

    # CSS
    css_blocks = await load_all_css(doc, url)
    rules = parse_css(css_blocks)
    computed = apply_css_to_dom(doc, rules)

    # DOM ROOTS
    roots = []
    for i, el in enumerate(doc.iterchildren()):
        if isinstance(el.tag, str):
            roots.append(build_tree(el, computed, 0, i))

    return {
        "meta": {
            "url": url,
            "title": title,
            "lang": lang,
            "charset": charset
        },
        "root_elements": [node_to_dict(r) for r in roots]
    }


# ============================================================
# TEST CALL
# ============================================================

async def main():
    data = await parse_url("https://example.com")
    if data:
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
