import json
from typing import Any, Dict
from app.utils.playwright_utils import get_browser

# ==========================================================
# JS для построения DOM JSON совместимого с ElementNode
# ==========================================================
BUILD_DOM_JS = r"""
() => {
    function extract(node, path = "body[1]") {
        if (!node) return null;

        // Текстовые узлы
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent.trim();
            if (!text) return null;
            return { tag: "#text", text, dom_path: path };
        }

        const obj = {
            tag: node.tagName?.toLowerCase() || "unknown",
            attributes: {},
            children: [],
            dom_path: path,
            styles: {},
            computed: {},
            pseudo: {}
        };

        // Атрибуты
        for (const attr of node.attributes || []) {
            obj.attributes[attr.name] = attr.value;
        }

        // Дети
        let indexMap = {};
        for (const child of node.children || []) {
            const tag = child.tagName?.toLowerCase() || "unknown";
            indexMap[tag] = (indexMap[tag] || 0) + 1;
            const childPath = `${path} > ${tag}[${indexMap[tag]}]`;
            const c = extract(child, childPath);
            if (c) obj.children.push(c);
        }

        return obj;
    }

    return extract(document.body);
}
"""

# ==========================================================
# БЕЗОПАСНЫЙ fetch_page()
# ==========================================================
async def fetch_page(url: str) -> dict:
    """
    Возвращает JSON строго в формате:
    {
        "document": {
            "url": "...",
            "title": "...",
            "lang": "...",
            "parse_errors": []
        },
        "dom": { ElementNode JSON }
    }
    """
    browser = await get_browser()
    page = await browser.new_page()

    try:
        # -----------------------------
        # Шаг 1: загрузка страницы
        # -----------------------------
        await page.goto(url, wait_until="load")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(500)  # небольшой буфер для динамики

        # -----------------------------
        # Шаг 2: безопасное получение DOM
        # -----------------------------
        dom = None
        for attempt in range(5):
            if page.main_frame.is_detached():
                raise RuntimeError("Frame is detached")
            try:
                dom = await page.evaluate(BUILD_DOM_JS)
                if dom:
                    break
            except Exception:
                await page.wait_for_timeout(300)
        else:
            raise RuntimeError("Не удалось получить DOM после 5 попыток")

        # -----------------------------
        # Шаг 3: получение информации о документе
        # -----------------------------
        # title
        title = await page.title()

        # lang (попробуем достать из <html lang="...">)
        try:
            lang = await page.evaluate("document.documentElement.lang || 'en'")
        except Exception:
            lang = "en"

        document_info = {
            "url": page.url,
            "title": title,
            "lang": lang,
            "parse_errors": []
        }

        return {
            "document": document_info,
            "dom": dom
        }

    finally:
        await page.close()

# ==========================================================
# SAFE DOM EXTRACTOR
# ==========================================================
async def safe_get_dom(page):
    if page.main_frame.is_detached():
        raise RuntimeError("Frame is detached")

    try:
        return await page.evaluate(BUILD_DOM_JS)
    except Exception:
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(150)
        return await page.evaluate(BUILD_DOM_JS)