import os
import sys
import tempfile
import atexit
import shutil

# =================================================================================
print("="*80, file=sys.stderr)
print("--- RUNNING FINAL VERSION OF text_feature_extractor.py ---", file=sys.stderr)
print("--- This version uses a TEMPORARY, RANDOM directory for the cache. ---", file=sys.stderr)
print("="*80, file=sys.stderr)
# =================================================================================

import tensorflow_hub as hub
import numpy as np
from pathlib import Path
from app.services.analytics.json_parser.models import DocumentModel, ElementNode

MODEL_URL = "https://tfhub.dev/google/universal-sentence-encoder/4"
VECTOR_SIZE = 512
TEMP_CACHE_DIR = None

def setup_model_cache():
    """
    Создает временную, уникальную директорию для кэша TensorFlow Hub
    и регистрирует ее для удаления при завершении работы программы.
    """
    global TEMP_CACHE_DIR
    try:
        # Создаем временную директорию с уникальным именем
        TEMP_CACHE_DIR = tempfile.mkdtemp(prefix="tfhub_cache_")
        os.environ['TFHUB_CACHE_DIR'] = TEMP_CACHE_DIR
        print(f"--- Using temporary cache directory: {TEMP_CACHE_DIR} ---", file=sys.stderr)
    except Exception as e:
        print(f"FATAL ERROR: Could not create temporary directory: {e}", file=sys.stderr)
        # Если даже это не удалось, прекращаем работу
        sys.exit(1)

def cleanup_cache():
    """Удаляет временную директорию кэша."""
    global TEMP_CACHE_DIR
    if TEMP_CACHE_DIR and os.path.exists(TEMP_CACHE_DIR):
        print(f"--- Cleaning up temporary cache directory: {TEMP_CACHE_DIR} ---", file=sys.stderr)
        shutil.rmtree(TEMP_CACHE_DIR, ignore_errors=True)

# Выполняем настройку кеша при импорте модуля
setup_model_cache()
# Регистрируем функцию очистки, которая будет вызвана при выходе из Python
atexit.register(cleanup_cache)


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
