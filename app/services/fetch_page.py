from typing import Dict, Any, List
from app.utils.playwright_utils import get_browser

async def fetch_page(url: str) -> Dict[str, Any]:
    browser = await get_browser()
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded")
        html_content = await page.content()

        elements_data: List[Dict[str, Any]] = []
        elements = await page.query_selector_all("*")

        for el in elements:
            # Get ARIA attributes
            aria_attrs = await el.evaluate("""
                e => {
                    const result = {};
                    for (const attr of e.getAttributeNames()) {
                        if (attr.startsWith('aria-')) result[attr] = e.getAttribute(attr);
                    }
                    return result;
                }
            """)

            # Get CSS styles relevant to visibility and color
            styles = await el.evaluate("""
                        e => {
                            const s = window.getComputedStyle(e);
                            return {
                                // Layout and positioning
                                display: s.display,
                                visibility: s.visibility,
                                position: s.position,
                                top: s.top,
                                left: s.left,
                                width: s.width,
                                height: s.height,
                                margin: s.margin,
                                padding: s.padding,

                                // Color and typography
                                color: s.color,
                                backgroundColor: s.backgroundColor,
                                fontSize: s.fontSize,
                                fontFamily: s.fontFamily,
                                fontWeight: s.fontWeight,
                                lineHeight: s.lineHeight,
                                letterSpacing: s.letterSpacing,
                                textTransform: s.textTransform,
                                textAlign: s.textAlign,
                                textDecoration: s.textDecoration,

                                // Accessibility hints
                                cursor: s.cursor,
                                outline: s.outline,
                                overflow: s.overflow,
                                opacity: s.opacity
                            };
                        }
                    """)

            # Base element info
            tag_name = await el.evaluate("e => e.tagName.toLowerCase()")
            role = await el.get_attribute("role")
            text = await el.inner_text()

            elements_data.append({
                "tag": tag_name,
                "id": await el.get_attribute("id"),
                "class": await el.get_attribute("class"),
                "role": role,
                "aria": aria_attrs,
                "attributes": {
                    "alt": await el.get_attribute("alt"),
                    "title": await el.get_attribute("title"),
                    "tabindex": await el.get_attribute("tabindex"),
                    "href": await el.get_attribute("href"),
                    "src": await el.get_attribute("src"),
                    "type": await el.get_attribute("type"),
                    "name": await el.get_attribute("name"),
                    "value": await el.get_attribute("value"),
                    "placeholder": await el.get_attribute("placeholder"),
                },
                "css": styles,
                "text": text.strip() if text else "",
            })

        return {
            "url": url,
            "summary": {
                "total_elements": len(elements_data),
                "interactive_elements": sum(1 for e in elements_data if e["role"] in ("button", "link", "textbox"))
            },
            "elements": elements_data,
        }

    finally:
        await page.close()
