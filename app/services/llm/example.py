import json
from app.services.llm.predictor import predict_usability

# 1. Загрузите ваш JSON (например, из файла или тела HTTP-запроса)
with open('debug_raw_data.json', 'r', encoding='utf-8') as f:
    site_data_json = json.load(f)

# 2. Вызовите функцию для получения предсказания
try:
    usability_score = predict_usability(site_data_json)
    print(f"Предсказанная оценка юзабилити: {usability_score:.2f}")
except (FileNotFoundError, ValueError) as e:
    print(f"Ошибка: {e}")
