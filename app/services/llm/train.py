import numpy as np
from tensorflow import keras
import os
from app.services.llm.data_loader import load_dataset
from app.services.llm.models import create_usability_model
from app.services.llm.feature_extractor.text_feature_extractor import setup_model_cache


def _prepare_batch_input(sample_x):
    batch_dict = {}
    for key, matrix in sample_x.items():
        batch_dict[key] = np.expand_dims(matrix, axis=0)
    return batch_dict


def train_model(epochs=100, batch_size=1):
    print("--- Этап 1: Настройка и загрузка данных ---")
    setup_model_cache()

    X_train, y_train = load_dataset()

    if len(X_train) == 0:
        print("Датасет пуст. Обучение прервано.")
        return

    print(f"Загружено {len(X_train)} примеров для обучения.")

    if batch_size > 1:
        print(f"Размер батча был > 1, но для данного режима он установлен в 1.")
        batch_size = 1

    print("\n--- Этап 2: Создание модели ---")
    model = create_usability_model()
    model.summary()

    print("\n--- Этап 3: Обучение модели ---")
    for epoch in range(epochs):
        total_loss = 0
        total_mae = 0

        indices = np.arange(len(X_train))
        np.random.shuffle(indices)

        for i, data_index in enumerate(indices):
            x_sample_dict = X_train[data_index]
            y_sample = y_train[data_index]

            x_batch = _prepare_batch_input(x_sample_dict)
            y_batch = np.array([y_sample])

            results = model.train_on_batch(x_batch, y_batch)

            loss = results[0]
            mae = results[1]

            total_loss += loss
            total_mae += mae

        avg_loss = total_loss / len(X_train)
        avg_mae = total_mae / len(X_train)
        
        print(f"Эпоха {epoch + 1}/{epochs} - Loss: {avg_loss:.4f}, MAE: {avg_mae:.4f}")

    print("\n--- Этап 4: Сохранение модели ---")
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_save_path = os.path.join(PROJECT_ROOT, 'trained_model.keras')
    model.save(model_save_path)
    print(f"Модель сохранена в: {model_save_path}")


if __name__ == '__main__':
    train_model(epochs=100)
