import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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


async def parse_url(url: str, selectors: list[str] | None = None) -> dict | None:
    """
    Основная функция парсера с улучшенной обработкой ошибок
    """
    try:
        html = await fetch_html(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # META SECTION (без изменений)
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

        result = {
            "meta": {
                "url": url,
                "title": title,
                "lang": lang,
                "charset": charset,
            },
            "elements": []
        }

        # ELEMENTS SECTION с улучшенной обработкой
        if selectors:
            unique_elements = set()

            for selector in selectors:
                try:
                    elements = soup.select(selector)
                    unique_elements.update(elements)
                except Exception as e:
                    print(f"Selector error '{selector}': {e}")
                    continue

            for el in unique_elements:
                try:
                    element_info = {
                        "tag": el.name,
                        "id": el.get("id", ""),
                        "classes": el.get("class", []),
                        "text": el.get_text(strip=True)[:500],  # ограничиваем длину текста
                        "attributes": {},
                        "computedStyles": {},
                    }

                    # атрибуты
                    for attr, value in el.attrs.items():
                        if attr == "class":
                            continue
                        # Сериализуем значения в строку для JSON
                        if isinstance(value, list):
                            element_info["attributes"][attr] = ' '.join(value)
                        else:
                            element_info["attributes"][attr] = str(value)

                    # inline computed styles
                    inline_css = el.get("style", "")
                    element_info["computedStyles"] = parse_inline_styles(inline_css)

                    result["elements"].append(element_info)

                except Exception as e:
                    print(f"Element parsing error: {e}")
                    continue

        return result

    except Exception as e:
        print(f"Parse URL error: {e}")
        return None
