import os
import sys

# =================================================================================
print("="*80, file=sys.stderr)
print("--- RUNNING LATEST VERSION OF text_feature_extractor.py ---", file=sys.stderr)
print("--- This version caches models in the USER'S HOME DIRECTORY. ---", file=sys.stderr)
print("="*80, file=sys.stderr)
# =================================================================================

import tensorflow_hub as hub
import numpy as np
from pathlib import Path
from app.services.analytics.json_parser.models import DocumentModel, ElementNode

MODEL_URL = "https://tfhub.dev/google/universal-sentence-encoder/4"
VECTOR_SIZE = 512

def setup_model_cache():
    """
    Настраивает директорию для кэширования моделей в домашней директории пользователя,
    чтобы избежать конфликтов внутри проекта.
    """
    try:
        # Используем Path.home() для получения домашней директории
        cache_dir = Path.home() / ".tfhub_cache_accessibility_analyzer"
        
        # Проверяем, не существует ли по этому пути файл
        if cache_dir.exists() and not cache_dir.is_dir():
            print(f"Warning: Found a file at the cache path {cache_dir}. Removing it.", file=sys.stderr)
            os.remove(cache_dir)
        
        # Создаем директорию, если она не существует
        os.makedirs(cache_dir, exist_ok=True)
        
        # Устанавливаем переменную окружения
        os.environ['TFHUB_CACHE_DIR'] = str(cache_dir)
        print(f"--- TensorFlow Hub cache directory is set to: {cache_dir} ---", file=sys.stderr)

    except Exception as e:
        print(f"FATAL ERROR in setup_model_cache: {e}", file=sys.stderr)
        # В случае ошибки используем временную директорию
        import tempfile
        fallback_dir = tempfile.mkdtemp()
        os.environ['TFHUB_CACHE_DIR'] = fallback_dir
        print(f"--- Fallback TF Hub cache directory is set to: {fallback_dir} ---", file=sys.stderr)


# Выполняем настройку кеша при импорте модуля
setup_model_cache()

def _flatten_and_extract_text(elements: list[ElementNode], embed):
    text_features = []
    for element in elements:
        text_parts = [
            element.text,
            element.alt,
            element.title,
            element.placeholder
        ]
        concatenated_text = " ".join(filter(None, text_parts)).strip()

        if concatenated_text:
            vector = embed([concatenated_text])[0].numpy()
        else:
            vector = np.zeros(VECTOR_SIZE)
        
        text_features.append(vector)

        children = element.children
        if children:
            text_features.extend(_flatten_and_extract_text(children, embed))

    return text_features

def extract_text_features(document_model: DocumentModel):
    elements = document_model.root.children
    if not elements:
        return np.array([])

    embed = hub.load(MODEL_URL)
    
    text_features = _flatten_and_extract_text(elements, embed)

    return np.array(text_features)

if __name__ == '__main__':
    import json
    from app.services.analytics.json_parser.models import DocumentFactory
    try:
        example_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dataset', '1.json')
        
        with open(example_json_path, 'r', encoding='utf-8') as f:
            json_string_content = f.read()
            
        parsed_data = json.loads(json_string_content)
        document_model = DocumentFactory.load_from_json(parsed_data)
        
        text_vectors = extract_text_features(document_model)
        
    except FileNotFoundError:
        pass
    except Exception as e:
        pass
