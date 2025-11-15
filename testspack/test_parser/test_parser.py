import pytest
import json
import os
from pathlib import Path
# Ваш импорт, который теперь указывает на асинхронный модуль
from app.services.accessibility.browser_to_json_parser import parse_url


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


@pytest.mark.asyncio
async def test_no_elements_found(local_server):
    """
    Проверяет, что парсер корректно возвращает пустой список, если ничего не найдено.
    """
    test_url = f"{local_server}/test_page.html"
    selectors = ['#non-existent-id', '.fake-class']
    data = await parse_url(test_url, selectors=selectors)

    assert data is not None
    # Теперь проверяем root_elements вместо elements
    assert len(data['root_elements']) == 0  # Должен вернуть пустой список корневых элементов


@pytest.mark.asyncio
async def test_invalid_url_handling():
    """
    Проверяет, что парсер возвращает None при ошибке (например, неверный URL).
    """
    data = await parse_url("http://thissitedoesnotexist.invalid")
    assert data is None


@pytest.mark.asyncio
async def test_tree_structure_parsing(local_server):
    """
    Проверяет, что парсер возвращает древовидную структуру с детьми.
    """
    test_url = f"{local_server}/test_page.html"
    data = await parse_url(test_url)

    assert data is not None
    assert 'root_elements' in data

    # Проверяем, что есть корневые элементы
    assert len(data['root_elements']) > 0

    # Проверяем структуру первого корневого элемента (обычно <html>)
    html_root = data['root_elements'][0]
    assert html_root['tag'] == 'html'
    assert 'children' in html_root
    assert len(html_root['children']) > 0

    # Проверяем наличие структурных полей
    assert 'depth' in html_root
    assert 'index' in html_root
    assert 'parent_id' in html_root


@pytest.mark.asyncio
async def test_element_filtering_with_selectors(local_server):
    """
    Проверяет фильтрацию элементов по селекторам с сохранением структуры.
    """
    test_url = f"{local_server}/test_page.html"
    selectors = ['a', 'img']
    data = await parse_url(test_url, selectors=selectors)

    assert data is not None
    assert len(data['root_elements']) > 0

    # Функция для рекурсивного поиска элементов по тегу
    def find_elements_by_tag(tree, tag):
        elements = []
        if tree['tag'] == tag:
            elements.append(tree)
        for child in tree.get('children', []):
            elements.extend(find_elements_by_tag(child, tag))
        return elements

    # Ищем все ссылки и изображения в дереве
    all_links = []
    all_images = []
    for root in data['root_elements']:
        all_links.extend(find_elements_by_tag(root, 'a'))
        all_images.extend(find_elements_by_tag(root, 'img'))

    # Проверяем, что нашли ожидаемые элементы
    assert len(all_links) >= 1  # Должна быть хотя бы одна ссылка
    assert len(all_images) >= 1  # Должно быть хотя бы одно изображение

    # Проверяем атрибуты найденных элементов
    link = all_links[0]
    assert link['attributes']['href'] == "#top"

    image = all_images[0]
    assert image['attributes']['src'] == "logo.png"
    assert image['attributes']['alt'] == "Test Logo"


@pytest.mark.asyncio
async def test_element_hierarchy_preservation(local_server):
    """
    Проверяет, что древовидная структура сохраняется при фильтрации.
    """
    test_url = f"{local_server}/test_page.html"
    # Фильтруем только ссылки, но должны сохранить их родительские контейнеры
    selectors = ['a']
    data = await parse_url(test_url, selectors=selectors)

    assert data is not None
    assert len(data['root_elements']) > 0

    # Проверяем, что структура сохранилась (ссылки находятся внутри своих родителей)
    def check_element_in_container(tree, target_tag):
        """Проверяет, что целевой элемент находится внутри контейнера"""
        for child in tree.get('children', []):
            if child['tag'] == target_tag:
                return True
            if check_element_in_container(child, target_tag):
                return True
        return False

    # Должны найти ссылки внутри древовидной структуры
    found_links = False
    for root in data['root_elements']:
        if check_element_in_container(root, 'a'):
            found_links = True
            break

    assert found_links, "Links should be preserved within tree structure"


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

    # 2. Проверяем древовидную структуру
    assert 'root_elements' in data
    assert len(data['root_elements']) > 0

    # 3. Сохраняем файл (это синхронная операция, и это нормально)
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        pytest.fail(f"Не удалось записать JSON-файл: {e}")

    # 4. Проверяем, что файл существует
    assert os.path.exists(output_filename), "JSON-файл не был создан!"

    # 5. Читаем файл обратно (тоже синхронно)
    with open(output_filename, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)

    assert saved_data['meta']['title'] == "Test Page Title"
    assert len(saved_data['root_elements']) > 0

    # 6. Ищем ссылку в древовидной структуре
    def find_element_in_tree(tree, tag):
        if tree['tag'] == tag:
            return tree
        for child in tree.get('children', []):
            result = find_element_in_tree(child, tag)
            if result:
                return result
        return None

    # Ищем ссылку в сохраненных данных
    link_el = None
    for root in saved_data['root_elements']:
        link_el = find_element_in_tree(root, 'a')
        if link_el:
            break

    assert link_el is not None
    assert link_el['attributes']['href'] == "#top"


@pytest.mark.asyncio
async def test_real_json_save_from_live_site():
    """
    Тест парсинга реального сайта с сохранением древовидной структуры.
    """
    live_url = "https://www.yahoo.com/"
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

    # Проверяем новую структуру данных
    assert "meta" in data
    assert "root_elements" in data  # Теперь root_elements вместо elements

    # Проверяем, что есть древовидная структура
    assert len(data['root_elements']) > 0, "No root elements found"

    # Проверяем наличие структурных полей в первом элементе
    first_root = data['root_elements'][0]
    assert 'tag' in first_root
    assert 'children' in first_root
    assert 'depth' in first_root
    assert 'parent_id' in first_root

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

        # Проверяем структуру загруженных данных
        assert "root_elements" in loaded_data
        assert len(loaded_data["root_elements"]) > 0

    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON saved: {e}")


@pytest.mark.asyncio
async def test_computed_styles_preservation(local_server):
    """
    Проверяет, что computedStyles корректно сохраняются в древовидной структуре.
    """
    test_url = f"{local_server}/test_page.html"
    data = await parse_url(test_url)

    assert data is not None

    # Функция для поиска элемента с inline стилями
    def find_element_with_styles(tree):
        if tree.get('computedStyles'):
            return tree
        for child in tree.get('children', []):
            result = find_element_with_styles(child)
            if result:
                return result
        return None

    # Ищем элемент со стилями
    styled_element = None
    for root in data['root_elements']:
        styled_element = find_element_with_styles(root)
        if styled_element:
            break

    # Если на странице есть элементы со стилями, проверяем их
    if styled_element:
        assert 'computedStyles' in styled_element
        assert isinstance(styled_element['computedStyles'], dict)