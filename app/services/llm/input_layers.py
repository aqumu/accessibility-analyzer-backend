# -*- coding: utf-8 -*-

"""
Определяет все входные слои (keras.Input) для мультимодальной модели.
"""
from tensorflow.keras import layers
import os
import sys

# Добавляем корень проекта в sys.path для импорта config
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.services.llm.config import FEATURE_MAPPING


def create_model_inputs(text_vector_size, numeric_vector_size, color_vector_size):
    """
    Создает и возвращает словарь Keras Input слоев.
    """

    # 1. Входы для предварительно рассчитанных векторов
    text_input = layers.Input(shape=(None, text_vector_size), name="text_input")
    numeric_input = layers.Input(shape=(None, numeric_vector_size), name="numeric_input")
    color_input = layers.Input(shape=(None, color_vector_size), name="color_input")

    # 2. Входы для категориальных признаков (подаются как индексы)
    categorical_inputs = {}
    for name in FEATURE_MAPPING.get("categorical", []):
        cat_input = layers.Input(shape=(None, 1), name=f"{name}_input")
        categorical_inputs[name] = cat_input

    # 3. Собираем все входы в один словарь
    all_inputs = {
        "text": text_input,
        "numeric": numeric_input,
        "color": color_input,
        **categorical_inputs
    }

    return all_inputs