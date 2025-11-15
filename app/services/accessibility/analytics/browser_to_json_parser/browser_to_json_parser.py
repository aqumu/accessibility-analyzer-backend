import json
import sys
# Используем async_api
from playwright.async_api import async_playwright, Page, ElementHandle
from typing import List, Dict, Any, Optional


# --- Вспомогательные асинхронные функции ---

async def get_element_depth(element: ElementHandle) -> int:
    """Вспомогательная функция для получения глубины вложенности DOM."""
    return await element.evaluate("""(el) => {
        let depth = 0;
        let current = el;
        while (current.parentElement) {
            depth++;
            current = current.parentElement;
        }
        return depth;
    }""")


async def get_specific_attributes(element: ElementHandle) -> Dict[str, Optional[str]]:
    """Получает только те атрибуты, что указаны в примере JSON."""
    return await element.evaluate("""(el) => {
        const attrs = [
            'src', 'alt', 'aria-label', 'aria-hidden', 'tabindex', 
            'href', 'for', 'type', 'placeholder'
        ];
        const result = {};
        for (const attr of attrs) {
            result[attr] = el.getAttribute(attr) || null;
        }
        return result;
    }""")


async def get_computed_styles(element: ElementHandle) -> Dict[str, Any]:
    """Получает вычисленные стили, как в примере."""
    try:
        styles = await element.evaluate("""(el) => {
            const style = window.getComputedStyle(el);
            return {
                fontSize: style.fontSize,
                fontWeight: style.fontWeight,
                lineHeight: style.lineHeight,
                color: style.color,
                backgroundColor: style.backgroundColor,
                display: style.display,
                position: style.position,
                opacity: style.opacity,
                visibility: style.visibility
            };
        }""")
        styles["contrastWithBackground"] = None  # Placeholder
        return styles
    except Exception:
        return {
            "fontSize": None, "fontWeight": None, "lineHeight": None,
            "color": None, "backgroundColor": None, "display": None,
            "position": None, "opacity": None, "visibility": None,
            "contrastWithBackground": None
        }


async def get_box_model(element: ElementHandle) -> Dict[str, Any]:
    """Получает геометрию элемента."""
    try:
        box = await element.bounding_box()
        if box:
            return {
                "width": box['width'],
                "height": box['height'],
                "top": box['top'],
                "left": box['left']
            }
        return {"width": 0, "height": 0, "top": 0, "left": 0}
    except Exception:
        return {"width": 0, "height": 0, "top": 0, "left": 0}


async def get_tree_info(element: ElementHandle) -> Dict[str, Any]:
    """Получает информацию о дереве DOM."""
    try:
        return {
            "depth": await get_element_depth(element),
            "parentTag": await element.evaluate(
                '(el) => el.parentElement ? el.parentElement.tagName.toLowerCase() : null'),
            "childrenTags": await element.evaluate(
                '(el) => Array.from(el.children).map(child => child.tagName.toLowerCase())')
        }
    except Exception:
        return {"depth": 0, "parentTag": None, "childrenTags": []}


async def get_accessibility_info(element: ElementHandle, tag: str) -> Dict[str, Any]:
    """Упрощенное получение данных о доступности."""
    role = await element.get_attribute('role')
    is_interactive = tag in ['a', 'button', 'input', 'select', 'textarea'] or \
                     role in ['button', 'link', 'checkbox', 'menuitem']

    return {
        "name": await element.get_attribute('aria-label') or None,
        "description": await element.get_attribute('aria-describedby') or None,
        "role": role or tag,
        "isInteractive": is_interactive
    }


async def get_interactivity_info(element: ElementHandle) -> Dict[str, Any]:
    """Упрощенное получение данных об интерактивности."""
    try:
        tab_index_str = await element.get_attribute('tabindex')
        tab_index_order = int(tab_index_str) if tab_index_str and tab_index_str.isdigit() else None

        is_focusable = await element.evaluate("""(el) => {
            try {
                el.focus();
                const focused = document.activeElement === el;
                if (focused) el.blur();
                return focused;
            } catch (e) {
                return false;
            }
        }""")

        return {
            "focusable": is_focusable,
            "keyboardAccessible": is_focusable,
            "tabIndexOrder": tab_index_order
        }
    except Exception:
        return {"focusable": None, "keyboardAccessible": None, "tabIndexOrder": None}


# --- Главная асинхронная функция ---

async def parse_url(url: str, selectors: List[str] = None) -> Optional[Dict[str, Any]]:
    """
    Главная асинхронная функция парсера.
    """

    if selectors is None:
        selectors = ['a', 'button', 'img', 'input', 'label', '[role="button"]']

    query_selector = ", ".join(selectors)

    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='load', timeout=60000)

            # 1. Meta Data
            meta_data = {
                "url": url,
                "title": await page.title(),
                "lang": await page.locator('html').get_attribute('lang') or None,
                "charset": await page.evaluate('() => document.characterSet') or "utf-8"
            }

            elements_data = []

            # 2. Elements Data
            elements = await page.locator(query_selector).all()
            print(f"Найдено {len(elements)} элементов по селекторам: {query_selector}")

            for el in elements:
                try:
                    tag = await el.evaluate('(el) => el.tagName.toLowerCase()')

                    element_info = {
                        "tag": tag,
                        "id": await el.get_attribute('id') or None,
                        "classes": (await el.get_attribute('class') or "").split(),
                        "role": await el.get_attribute('role') or None,
                        "text": (await el.text_content(timeout=500) or "").strip(),
                        "html": await el.evaluate('(el) => el.outerHTML', timeout=500),

                        "attributes": await get_specific_attributes(el),
                        "computedStyles": await get_computed_styles(el),
                        "box": await get_box_model(el),
                        "interactivity": await get_interactivity_info(el),
                        "accessibility": await get_accessibility_info(el, tag),
                        "tree": await get_tree_info(el)
                    }
                    elements_data.append(element_info)

                except Exception as e:
                    print(f"Не удалось обработать элемент: {e}", file=sys.stderr)

            await browser.close()

            return {
                "meta": meta_data,
                "elements": elements_data
            }

        except Exception as e:
            print(f"Ошибка во время парсинга URL {url}: {e}", file=sys.stderr)
            if browser:
                await browser.close()
            return None