import json
import os
import numpy as np
from app.services.analytics.json_parser.models import DocumentFactory
from app.services.llm.feature_extractor.text_feature_extractor import extract_text_features
from app.services.llm.feature_extractor.numeric_feature_extractor import extract_numeric_features
from app.services.llm.feature_extractor.color_feature_extractor import extract_color_features
from app.services.llm.feature_extractor.categorical_feature_extractor import extract_categorical_features


def load_dataset(dataset_dir=None, labels_file='labels.json'):
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if dataset_dir is None:
        dataset_dir = os.path.join(PROJECT_ROOT, 'dataset')

    labels_path = os.path.join(dataset_dir, labels_file)

    try:
        with open(labels_path, 'r', encoding='utf-8') as f:
            labels = json.load(f)
    except FileNotFoundError:
        return [], np.array([])

    X_list = []
    y_list = []

    for filename, score in labels.items():
        file_path = os.path.join(dataset_dir, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_string_content = f.read()
            
            parsed_data = json.loads(json_string_content)
            document_model = DocumentFactory.load_from_json(parsed_data)

            text_vectors = extract_text_features(document_model)

            if text_vectors.shape[0] == 0:
                continue

            num_elements = text_vectors.shape[0]

            color_vectors, contrast_vectors = extract_color_features(document_model)

            numeric_vectors = extract_numeric_features(document_model, normalize=False)

            if contrast_vectors.shape[0] == numeric_vectors.shape[0]:
                numeric_vectors = np.concatenate([numeric_vectors, contrast_vectors], axis=1)

            categorical_dict = extract_categorical_features(document_model)

            all_shapes_match = True
            if not (text_vectors.shape[0] == numeric_vectors.shape[0] == color_vectors.shape[0]):
                all_shapes_match = False
            for cat_name, cat_array in categorical_dict.items():
                if cat_array.shape[0] != num_elements:
                    all_shapes_match = False

            if not all_shapes_match:
                continue

            model_input_dict = {
                "text_input": text_vectors,
                "numeric_input": numeric_vectors,
                "color_input": color_vectors
            }
            for cat_name, cat_array in categorical_dict.items():
                model_input_dict[f"{cat_name}_input"] = cat_array

            X_list.append(model_input_dict)
            y_list.append(score)

        except FileNotFoundError:
            continue
        except Exception as e:
            continue

    if not X_list:
        return [], np.array([])

    return X_list, np.array(y_list, dtype=np.float32)


if __name__ == '__main__':
    from feature_extractor.text_feature_extractor import setup_model_cache

    setup_model_cache()

    X_data, y_data = load_dataset()
