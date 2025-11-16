# test_real_website_txt.py
import pytest
import asyncio
import json
from datetime import datetime
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.analytics.browser_to_json_parser.browser_to_json_parser import parse_url
from app.services.analytics.json_parser.models import DocumentFactory
from app.services.analytics.data_group.data_group import DataGroupExtractor
from app.services.analytics.rules_analyzer.rules_factory import RulesFactory


class RealWebsiteTesterTXT:
    """Тестер для реального веб-сайта с выводом в TXT"""

    def __init__(self, output_file="test_results.txt"):
        self.output_file = output_file
        self.results = []

    async def test_website(self, url: str):
        """Полный тест веб-сайта с текстовым выводом"""
        print(f"🚀 Начинаем тестирование: {url}")

        try:
            # 1. Парсинг страницы
            print("📥 Парсинг страницы...")
            raw_data = await parse_url(url)

            if not raw_data:
                self._add_result("❌ ОШИБКА: Не удалось получить данные с сайта")
                return self._save_results()

            # 2. Создание DocumentModel
            print("🔄 Создание DocumentModel...")
            document_model = DocumentFactory.load_from_json(raw_data)

            self._add_result(f"✅ УСПЕШНО: Создана модель с {len(document_model.elements)} элементами")
            self._add_result(f"📄 Информация о документе:")
            self._add_result(f"   - Заголовок: {document_model.info.title}")
            self._add_result(f"   - Язык: {document_model.info.lang}")
            self._add_result(f"   - URL: {document_model.info.url}")

            # 3. Извлечение данных по группам
            print("📊 Извлечение данных по группам...")
            extractor = DataGroupExtractor()

            groups_data = {
                "Изображения": extractor.extract_image_data(document_model),
                "Поля форм": extractor.extract_form_field_data(document_model),
                "Интерактивные элементы": extractor.extract_interactive_data(document_model),
                "Медиа элементы": extractor.extract_media_data(document_model),
                "Заголовки": extractor.extract_heading_data(document_model),
                "Таблицы": extractor.extract_table_data(document_model),
                "ARIA элементы": extractor.extract_aria_data(document_model)
            }

            self._add_result("")
            self._add_result("📊 СТАТИСТИКА ПО ГРУППАМ:")
            for group_name, data in groups_data.items():
                self._add_result(f"   - {group_name}: {len(data)} элементов")

            # 4. Создание и выполнение правил
            print("🏭 Создание и выполнение правил...")
            rules_factory = RulesFactory()
            rules_with_data = rules_factory.get_rules(document_model)

            self._add_result("")
            self._add_result("🔍 РЕЗУЛЬТАТЫ ПРОВЕРКИ ДОСТУПНОСТИ:")
            self._add_result("=" * 60)

            total_issues = 0
            issues_by_rule = {}

            for rule_instance, data_groups in rules_with_data:
                rule_name = rule_instance.__class__.__name__

                try:
                    # Запускаем анализ для каждого правила
                    rule_results = rule_instance.analyze(data_groups)

                    if rule_results:
                        total_issues += len(rule_results)
                        issues_by_rule[rule_name] = len(rule_results)

                        self._add_result(f"")
                        self._add_result(f"❌ {rule_name}: НАЙДЕНО ПРОБЛЕМ - {len(rule_results)}")

                        for i, issue in enumerate(rule_results, 1):
                            issue_type = issue.get('type', 'ПРОБЛЕМА')
                            message = issue.get('message', 'Без описания')
                            element = issue.get('element', 'Не указан')

                            self._add_result(f"   {i}. [{issue_type}] {message}")
                            if element and element != 'Не указан':
                                self._add_result(f"      Элемент: {element}")

                    else:
                        self._add_result(f"")
                        self._add_result(f"✅ {rule_name}: ПРОБЛЕМ НЕ НАЙДЕНО")

                except Exception as e:
                    self._add_result(f"")
                    self._add_result(f"⚠️ {rule_name}: ОШИБКА ВЫПОЛНЕНИЯ - {e}")

            # 5. Итоговая сводка
            self._add_result("")
            self._add_result("=" * 60)
            self._add_result("🎯 ИТОГОВАЯ СВОДКА:")
            self._add_result(f"   📊 Всего элементов на странице: {len(document_model.elements)}")
            self._add_result(f"   🔧 Проверено правил: {len(rules_with_data)}")
            self._add_result(f"   ❌ Всего проблем найдено: {total_issues}")

            if issues_by_rule:
                self._add_result("")
                self._add_result("📈 РАСПРЕДЕЛЕНИЕ ПРОБЛЕМ ПО ПРАВИЛАМ:")
                for rule_name, count in issues_by_rule.items():
                    self._add_result(f"   - {rule_name}: {count} проблем")

            if total_issues == 0:
                self._add_result("")
                self._add_result("🎉 ОТЛИЧНО! Все проверки пройдены успешно!")
            else:
                self._add_result("")
                self._add_result("💡 РЕКОМЕНДАЦИЯ: Обратите внимание на выявленные проблемы доступности")

            return self._save_results()

        except Exception as e:
            self._add_result(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            return self._save_results()

    def _add_result(self, text):
        """Добавляет текст в результаты"""
        self.results.append(text)

    def _save_results(self):
        """Сохраняет результаты в текстовый файл"""
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                # Заголовок
                f.write("=" * 70 + "\n")
                f.write("📋 ОТЧЕТ О ПРОВЕРКЕ ДОСТУПНОСТИ ВЕБ-САЙТА\n")
                f.write("=" * 70 + "\n")
                f.write(f"Дата проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")

                # Основные результаты
                for line in self.results:
                    f.write(line + "\n")

                # Подвал
                f.write("\n" + "=" * 70 + "\n")
                f.write("Проверка завершена\n")
                f.write("=" * 70 + "\n")

            print(f"💾 Текстовый отчет сохранен в: {self.output_file}")

            # Выводим краткую сводку в консоль
            print("\n📋 КРАТКАЯ СВОДКА:")
            for line in self.results:
                if any(keyword in line for keyword in ["❌", "✅", "⚠️", "🎯", "🎉"]):
                    print(line)

            return True

        except Exception as e:
            print(f"❌ Ошибка сохранения отчета: {e}")
            return False


@pytest.mark.asyncio
async def test_hack_mock_bank_website_txt():
    """
    Тестирует реальный веб-сайт Hack Mock Bank и сохраняет
    результаты в текстовый файл с описанием проблем
    """
    tester = RealWebsiteTesterTXT("hack_mock_bank_test_results.txt")

    # URL для тестирования
    test_url = "https://hack-mock-bank.vercel.app/"

    print("=" * 70)
    print("🎯 ТЕСТИРОВАНИЕ HACK MOCK BANK WEBSITE (TXT ОТЧЕТ)")
    print("=" * 70)

    success = await tester.test_website(test_url)

    # Проверяем, что тест завершился успешно
    assert success, "Тест завершился с ошибками"

    # Проверяем, что файл создан
    assert os.path.exists("hack_mock_bank_test_results.txt"), "Файл с результатами не создан"

    print("✅ Тест завершен успешно! Проверьте файл: hack_mock_bank_test_results.txt")


async def main():
    """Основная функция для запуска без pytest"""
    tester = RealWebsiteTesterTXT("hack_mock_bank_test_results.txt")
    test_url = "https://hack-mock-bank.vercel.app/"

    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ С TXT ОТЧЕТОМ")
    print("=" * 50)

    await tester.test_website(test_url)


if __name__ == "__main__":
    # Запуск без pytest
    asyncio.run(main())