import tensorflow_hub as hub
import numpy as np
import os
from app.services.analytics.json_parser.models import DocumentModel, ElementNode

MODELS_DIR = '.tfhub_cache'  # Изменено с 'models' для избежания конфликтов
MODEL_URL = "https://tfhub.dev/google/universal-sentence-encoder/4"
VECTOR_SIZE = 512

def setup_model_cache():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_dir = os.path.join(base_dir, MODELS_DIR)
    
    os.makedirs(cache_dir, exist_ok=True)
    os.environ['TFHUB_CACHE_DIR'] = cache_dir

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
        setup_model_cache()
        
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
