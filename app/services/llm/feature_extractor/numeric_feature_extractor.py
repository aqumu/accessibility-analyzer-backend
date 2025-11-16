import numpy as np
from sklearn.preprocessing import StandardScaler
import os
import json
from app.services.analytics.json_parser.models import DocumentModel, ElementNode
from app.services.llm.config import FEATURE_MAPPING


def _parse_css_value(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.lower().strip()
        if value == 'auto':
            return 0.0
        try:
            return float(''.join(filter(lambda x: x.isdigit() or x == '.', value)))
        except (ValueError, TypeError):
            return 0.0
    return 0.0


def _flatten_and_extract(elements: list[ElementNode], depth=0):
    all_features = []
    numeric_feature_keys = FEATURE_MAPPING.get("numeric_scalar", [])

    for element in elements:
        features = []
        for key in numeric_feature_keys:
            if key in ["depth", "num_children"]:
                continue
            
            value = getattr(element, key, None)
            features.append(_parse_css_value(value))

        children = element.children
        features.append(float(depth))
        features.append(float(len(children)))

        all_features.append(features)

        if children:
            all_features.extend(_flatten_and_extract(children, depth + 1))

    return all_features


def extract_numeric_features(document_model: DocumentModel, normalize=True):
    elements = document_model.root.children
    if not elements:
        return np.array([])

    feature_matrix = _flatten_and_extract(elements)
    feature_matrix = np.array(feature_matrix, dtype=np.float32)

    if normalize and feature_matrix.shape[0] > 0:
        scaler = StandardScaler()
        feature_matrix = scaler.fit_transform(feature_matrix)

    return feature_matrix


if __name__ == '__main__':
    from app.services.accessibility.json_parser import DocumentFactory
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        example_json_path = os.path.join(PROJECT_ROOT, 'dataset', '1.json')

        with open(example_json_path, 'r', encoding='utf-8') as f:
            json_string_content = f.read()
            
        parsed_data = json.loads(json_string_content)
        document_model = DocumentFactory.load_from_json(parsed_data)

        numeric_vectors = extract_numeric_features(document_model, normalize=True)

    except FileNotFoundError:
        pass
    except Exception as e:
        pass
