import pytest
import pytest_asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Dict

# ==========================================================
# Константа с полным путем к модулю (только один раз)
# ==========================================================
MODULE_PATH = "app.services.accessibility.analytics.browser_to_json_parser.browser_to_json_parser"

# ==========================================================
# Импортируем функции
# ==========================================================
try:
    mod = __import__(MODULE_PATH, fromlist=["fetch_page", "safe_get_dom", "BUILD_DOM_JS"])
    fetch_page = mod.fetch_page
    safe_get_dom = mod.safe_get_dom
    BUILD_DOM_JS = mod.BUILD_DOM_JS
except ImportError:
    print(f"Не удалось импортировать {MODULE_PATH}, используются заглушки.")

    BUILD_DOM_JS = "() => {}"

    async def fetch_page(url: str) -> Dict[str, Any]:
        return {}

    async def safe_get_dom(page):
        return {}

# ==========================================================
# Вспомогательная функция для создания мок-страницы
# ==========================================================
def create_mock_page():
    page = AsyncMock()
    page.url = "https://mock.com"
    page.title.return_value = "Mock Title"
    page.evaluate.return_value = {"tag": "body", "children": []}

    page.main_frame = MagicMock()
    page.main_frame.is_detached.return_value = False
    return page

def create_mock_browser(mock_page):
    browser = AsyncMock()
    browser.new_page.return_value = mock_page
    return browser

@pytest.mark.asyncio
async def test_fetch_page_success():
    mock_page = AsyncMock()
    mock_dom = {
        "tag": "body",
        "attributes": {},
        "children": [],
        "dom_path": "body[1]",
        "styles": {},
        "computed": {},
        "pseudo": {}
    }

    # evaluate возвращает DOM сразу
    mock_page.evaluate.return_value = mock_dom
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Example"
    mock_page.main_frame = MagicMock()
    mock_page.main_frame.is_detached.return_value = False

    mock_browser = AsyncMock()
    mock_browser.new_page.return_value = mock_page

    with patch(f"{MODULE_PATH}.get_browser", new_callable=AsyncMock) as mock_get_browser:
        mock_get_browser.return_value = mock_browser

        result = await fetch_page("https://example.com")

    # Проверяем вызовы
    mock_page.goto.assert_called_with("https://example.com", wait_until="load")
    mock_page.wait_for_load_state.assert_called_with("networkidle")
    # evaluate может быть вызван 1+ раз, но результат успешный
    assert mock_page.evaluate.call_count >= 1
    mock_page.close.assert_called_once()

    # Проверяем результат
    assert result["dom"]["tag"] == "body"
    assert result["dom"]["dom_path"] == "body[1]"


@pytest.mark.asyncio
async def test_fetch_page_evaluate_retry_success():
    mock_page = AsyncMock()
    mock_dom = {"tag": "body", "children": [{"tag": "div"}]}

    # 2 ошибки, потом успешный результат
    mock_page.evaluate.side_effect = [
        Exception("JS error 1"),
        Exception("JS error 2"),
        mock_dom
    ]
    mock_page.url = "https://retry-me.com"
    mock_page.title.return_value = "Retry Example"
    mock_page.main_frame = MagicMock()
    mock_page.main_frame.is_detached.return_value = False

    mock_browser = AsyncMock()
    mock_browser.new_page.return_value = mock_page

    with patch(f"{MODULE_PATH}.get_browser", new_callable=AsyncMock) as mock_get_browser:
        mock_get_browser.return_value = mock_browser

        result = await fetch_page("https://retry-me.com")

    assert mock_page.evaluate.call_count == 4
    assert result["dom"] == mock_dom
    assert result["document"]["lang"] == "en"
    mock_page.close.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_page_evaluate_fails_all_attempts():
    mock_page = create_mock_page()
    mock_page.evaluate.side_effect = [Exception(f"JS error {i}") for i in range(5)]
    mock_browser = create_mock_browser(mock_page)

    with patch(f"{MODULE_PATH}.get_browser", new_callable=AsyncMock) as mock_get_browser:
        mock_get_browser.return_value = mock_browser
        with pytest.raises(RuntimeError, match="Не удалось получить DOM после 5 попыток"):
            await fetch_page("https://fail-me.com")

    assert mock_page.evaluate.call_count == 5
    mock_page.close.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_page_frame_detached():
    mock_page = create_mock_page()
    mock_page.main_frame.is_detached.return_value = True
    mock_browser = create_mock_browser(mock_page)

    with patch(f"{MODULE_PATH}.get_browser", new_callable=AsyncMock) as mock_get_browser:
        mock_get_browser.return_value = mock_browser
        with pytest.raises(RuntimeError, match="Frame is detached"):
            await fetch_page("https://detached.com")

    mock_page.close.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_page_goto_fails():
    mock_page = create_mock_page()
    mock_page.goto.side_effect = Exception("Network timeout")
    mock_browser = create_mock_browser(mock_page)

    with patch(f"{MODULE_PATH}.get_browser", new_callable=AsyncMock) as mock_get_browser:
        mock_get_browser.return_value = mock_browser
        with pytest.raises(Exception, match="Network timeout"):
            await fetch_page("https://timeout.com")

    mock_page.close.assert_called_once()
    mock_page.evaluate.assert_not_called()

# ==========================================================
# Тесты safe_get_dom без фикстур
# ==========================================================
@pytest.mark.asyncio
async def test_safe_get_dom_success():
    mock_page = create_mock_page()
    mock_page.evaluate.return_value = {"tag": "html"}

    result = await safe_get_dom(mock_page)

    assert result == {"tag": "html"}
    mock_page.evaluate.assert_called_once_with(BUILD_DOM_JS)


@pytest.mark.asyncio
async def test_safe_get_dom_retry_success():
    mock_page = create_mock_page()
    mock_dom = {"tag": "success"}
    mock_page.evaluate.side_effect = [Exception("JS error 1"), mock_dom]

    result = await safe_get_dom(mock_page)

    assert result == mock_dom
    assert mock_page.evaluate.call_count == 2


@pytest.mark.asyncio
async def test_safe_get_dom_fails_both():
    mock_page = create_mock_page()
    mock_page.evaluate.side_effect = [Exception("JS error 1"), Exception("JS error 2")]

    with pytest.raises(Exception, match="JS error 2"):
        await safe_get_dom(mock_page)

    assert mock_page.evaluate.call_count == 2


@pytest.mark.asyncio
async def test_safe_get_dom_frame_detached():
    mock_page = create_mock_page()
    mock_page.main_frame.is_detached.return_value = True

    with pytest.raises(RuntimeError, match="Frame is detached"):
        await safe_get_dom(mock_page)

    mock_page.evaluate.assert_not_called()

# ==========================================================
# Интеграционный тест — остаётся без изменений
# ==========================================================
@pytest.mark.asyncio
@pytest.mark.integration
async def test_dump_real_dom_json():
    from app.utils.playwright_utils import startup_browser

    await startup_browser()

    url = "https://en.wikipedia.org/wiki/Cat"
    result = await fetch_page(url)

    assert isinstance(result, dict)
    assert "dom" in result
    assert "document" in result

    with open("example_dom.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n[OK] JSON сохранён в example_dom.json")
