# Accessibility Analyzer API

## Описание

Это бэкенд-сервис для анализа веб-страниц на соответствие рекомендациям по обеспечению доступности веб-контента (WCAG). API позволяет пользователям отправлять URL-адреса для анализа и получать подробные отчеты о нарушениях доступности.

## Основные возможности

- Асинхронный анализ веб-страниц.
- Проверка на соответствие правилам WCAG.
- Генерация отчетов с подробным описанием нарушений.
- Отслеживание статуса анализа.
- Аутентификация пользователей по токену.
- Предсказание оценки юзабилити с помощью нейросети.

## Технологический стек

- **Python 3.10**
- **FastAPI** для создания API.
- **Pydantic** для валидации данных.
- **SQLAlchemy** (предположительно, для работы с базой данных).
- **Alembic** (предположительно, для миграций базы данных).
- **CatBoost** для предсказания юзабилити.

## Установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone <URL-репозитория>
   cd accessibility-analyzer-backend
   ```

2. **Создайте и активируйте виртуальное окружение:**
   ```bash
   python -m venv venv
   venv/Scripts/activate  # source venv\bin\activate
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Запустите приложение:**
   ```bash
   uvicorn app.main:app --reload
   ```

   Приложение будет доступно по адресу `http://127.0.0.1:8000`.

## Использование API

### Эндпоинты

- `POST /api/analyzer/webpages/analyze`: Запустить анализ новой веб-страницы.
- `GET /api/analyzer/runs/{run_id}`: Получить статус и результат анализа.
- `GET /api/analyzer/webpages/{webpage_id}/runs`: Получить список всех анализов для конкретной веб-страницы.

### Пример запроса

**Запуск анализа:**

```bash
curl -X POST "http://127.0.0.1:8000/api/analyzer/webpages/analyze" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <ваш-токен>" \
     -d '{
       "url": "https://example.com"
     }'
```

**Получение статуса анализа:**

```bash
curl -X GET "http://127.0.0.1:8000/api/analyzer/runs/{run_id}" \
     -H "Authorization: Bearer <ваш-токен>"
```

## Предсказание юзабилити с помощью нейросети

В проекте используется модель CatBoost для предсказания оценки юзабилити сайта на основе его структуры.

### Пример использования

```python
import json
from app.services.llm.predictor import predict_usability

# 1. Загрузите JSON с данными сайта
with open('path/to/your/site_data.json', 'r', encoding='utf-8') as f:
    site_data_json = json.load(f)

# 2. Вызовите функцию для получения предсказания
try:
    usability_score = predict_usability(site_data_json)
    print(f"Предсказанная оценка юзабилити: {usability_score:.2f}")
except (FileNotFoundError, ValueError) as e:
    print(f"Ошибка: {e}")
```

**Примечание:** Функция `predict_usability` ожидает на вход JSON, содержащий определенную структуру данных сайта. Пример такой структуры можно найти в `app/services/dataset/`.
