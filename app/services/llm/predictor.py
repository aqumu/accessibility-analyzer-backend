import os
import numpy as np
from tensorflow import keras
import json
from typing import Dict, Any

from app.services.accessibility.analytics.json_parser.models import DocumentFactory
from app.services.llm.feature_extractor.text_feature_extractor import extract_text_features, setup_model_cache
from app.services.llm.feature_extractor.numeric_feature_extractor import extract_numeric_features
from app.services.llm.feature_extractor.color_feature_extractor import extract_color_features
from app.services.llm.feature_extractor.categorical_feature_extractor import extract_categorical_features

# --- Глобальные переменные для модели ---
_model = None
MODEL_PATH = None


def _get_model_path() -> str:
    """Определяет абсолютный путь к сохраненной модели."""
    global MODEL_PATH
    if MODEL_PATH is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MODEL_PATH = os.path.join(project_root, 'trained_model.keras')
    return MODEL_PATH


def _load_model():
    """Загружает модель Keras в память. Использует глобальную переменную для кэширования."""
    global _model
    if _model is None:
        model_path = _get_model_path()
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Обученная модель не найдена по пути: {model_path}. "
                                    f"Пожалуйста, сначала обучите модель, запустив train.py.")
        
        # Настройка кэша для TF-Hub модели перед загрузкой основной модели
        print("--- Настройка кэша для TF-Hub модели ---")
        setup_model_cache()
        
        print(f"--- Загрузка модели из {model_path} ---")
        _model = keras.models.load_model(model_path)
        print("--- Модель успешно загружена ---")


def _prepare_input_for_prediction(features: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """Добавляет batch-измерение к каждому массиву признаков."""
    return {key: np.expand_dims(value, axis=0) for key, value in features.items()}


def predict_usability(site_json: Dict[str, Any]) -> float:
    """
    Загружает модель и предсказывает оценку юзабилити для JSON-представления сайта.

    Args:
        site_json (Dict[str, Any]): Словарь, полученный из JSON-файла сайта.

    Returns:
        float: Предсказанная оценка юзабилити (от 0 до 10).
    """
    _load_model()  # Загружаем модель, если она еще не в памяти

    # 1. Парсинг JSON в DocumentModel
    document_model = DocumentFactory.load_from_json(site_json)

    # 2. Извлечение признаков (аналогично data_loader.py)
    text_vectors = extract_text_features(document_model)
    if text_vectors.shape[0] == 0:
        print("На странице не найдено текстовых элементов для анализа. Возвращена оценка 0.0.")
        return 0.0

    num_elements = text_vectors.shape[0]
    color_vectors, contrast_vectors = extract_color_features(document_model)
    numeric_vectors = extract_numeric_features(document_model, normalize=False)
    
    if contrast_vectors.shape[0] == numeric_vectors.shape[0]:
        numeric_vectors = np.concatenate([numeric_vectors, contrast_vectors], axis=1)

    categorical_dict = extract_categorical_features(document_model)

    # Проверка совпадения размерностей
    all_shapes_match = (
        text_vectors.shape[0] == numeric_vectors.shape[0] == color_vectors.shape[0] and
        all(cat_array.shape[0] == num_elements for cat_array in categorical_dict.values())
    )

    if not all_shapes_match:
        raise ValueError("Размеры извлеченных признаков не совпадают. Невозможно выполнить предсказание.")

    # 3. Формирование словаря для входа в модель
    model_input_dict = {
        "text_input": text_vectors,
        "numeric_input": numeric_vectors,
        "color_input": color_vectors,
        **{f"{cat_name}_input": cat_array for cat_name, cat_array in categorical_dict.items()}
    }

    # 4. Подготовка данных для предсказания (добавление batch-измерения)
    batch_input = _prepare_input_for_prediction(model_input_dict)

    # 5. Выполнение предсказания
    prediction = _model.predict(batch_input)

    # 6. Возврат результата
    return float(prediction[0][0])