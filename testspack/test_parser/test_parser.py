import pytest
import json
import os
from pathlib import Path
# Ваш импорт, который теперь указывает на асинхронный модуль
from app.services.accessibility.analytics.browser_to_json_parser.browser_to_json_parser import parse_url


# --- Тесты функциональности (Асинхронные) ---

@pytest.mark.asyncio
async def test_meta_data_parsing(local_server):
    """
    Проверяет, что мета-данные (title, lang, charset) парсятся корректно.
    """
    test_url = f"{local_server}/test_page.html"
    data = await parse_url(test_url)

    assert data is not None
    assert data['meta']['url'] == test_url
    assert data['meta']['title'] == "Test Page Title"
    assert data['meta']['lang'] == "en"
    assert data['meta']['charset'] == "UTF-8"


# @pytest.mark.asyncio
# async def test_element_parsing(local_server):
#     """
#     Проверяет, что конкретные элементы парсятся с правильными атрибутами.
#     """
#     test_url = f"{local_server}/test_page.html"
#     selectors = ['#logo', '#btn-submit']
#     data = await parse_url(test_url, selectors=selectors)
#
#     assert data is not None
#     assert len(data['elements']) == 2
#
#     # Находим логотип
#     logo = next((el for el in data['elements'] if el['id'] == 'logo'), None)
#     assert logo is not None
#     assert logo['tag'] == 'img'
#     assert 'header-logo' in logo['classes']
#     assert logo['attributes']['alt'] == "Test Logo"
#
#     # Находим кнопку
#     button = next((el for el in data['elements'] if el['id'] == 'btn-submit'), None)
#     assert button is not None
#     assert button['tag'] == 'button'
#     assert button['text'] == "Отправить"
#     assert button['computedStyles']['color'] == "rgb(255, 0, 0)"


@pytest.mark.asyncio
async def test_no_elements_found(local_server):
    """
    Проверяет, что парсер корректно возвращает пустой список, если ничего не найдено.
    """
    test_url = f"{local_server}/test_page.html"
    selectors = ['#non-existent-id', '.fake-class']
    data = await parse_url(test_url, selectors=selectors)

    assert data is not None
    assert len(data['elements']) == 0


@pytest.mark.asyncio
async def test_invalid_url_handling():
    """
    Проверяет, что парсер возвращает None при ошибке (например, неверный URL).
    """
    data = await parse_url("http://thissitedoesnotexist.invalid")
    assert data is None


# --- Тест, который реально сохраняет файл (Асинхронный) ---

@pytest.mark.asyncio
async def test_real_json_save(local_server, tmp_path):
    """
    Этот тест выполняет парсинг и РЕАЛЬНО сохраняет результат
    во временную папку (tmp_path), а затем проверяет содержимое файла.
    """
    print(f"\nФайлы будут сохранены в: {tmp_path}")
    test_url = f"{local_server}/test_page.html"
    output_filename = tmp_path / "saved_data.json"

    # 1. Запускаем парсер (асинхронно)
    data = await parse_url(test_url, selectors=['a', 'img'])

    assert data is not None
    assert len(data['elements']) == 2  # Нашли <img> и <a>

    # 2. Сохраняем файл (это синхронная операция, и это нормально)
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        pytest.fail(f"Не удалось записать JSON-файл: {e}")

    # 3. Проверяем, что файл существует
    assert os.path.exists(output_filename), "JSON-файл не был создан!"

    # 4. Читаем файл обратно (тоже синхронно)
    with open(output_filename, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)

    assert saved_data['meta']['title'] == "Test Page Title"
    assert len(saved_data['elements']) == 2

    link_el = next((el for el in saved_data['elements'] if el['tag'] == 'a'), None)
    assert link_el is not None
    assert link_el['attributes']['href'] == "#top"


@pytest.mark.asyncio
async def test_real_json_save_from_live_site():
    live_url = "https://wwe2.glitch.me"
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)

    output_filename = output_dir / "hack_bank_data.json"

    # Упрощаем селекторы для теста
    selectors_to_parse = [
        "header", "main", "footer", "nav",
        "h1", "h2", "h3",
        "a", "button", "img"
    ]

    data = await parse_url(live_url, selectors=selectors_to_parse)

    # Проверяем, что данные получены
    assert data is not None, "Failed to fetch and parse data"

    # Проверяем структуру данных
    assert "meta" in data
    assert "elements" in data

    # Сохраняем с обработкой ошибок сериализации
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        pytest.fail(f"Failed to save JSON: {e}")

    assert output_filename.exists()
    assert output_filename.stat().st_size > 0

    # Проверяем, что файл содержит валидный JSON
    try:
        with open(output_filename, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data is not None
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON saved: {e}")