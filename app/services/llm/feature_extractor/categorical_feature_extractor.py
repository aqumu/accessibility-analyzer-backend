import numpy as np
from app.services.accessibility.json_parser import DocumentModel, ElementNode
from app.services.llm.config import FEATURE_MAPPING, CATEGORICAL_VOCABULARIES


def _build_vocab_map(vocab_list):
    return {value: i + 1 for i, value in enumerate(vocab_list)}


VOCAB_MAPS = {
    key: _build_vocab_map(CATEGORICAL_VOCABULARIES[key])
    for key in FEATURE_MAPPING.get("categorical", [])
}
UNK_INDEX = 0


def _flatten_and_extract_cats(elements: list[ElementNode]):
    all_features = []
    categorical_keys = FEATURE_MAPPING.get("categorical", [])

    for element in elements:
        features = {}
        for key in categorical_keys:
            value = getattr(element, key, "")
            value = str(value).lower().strip()
            features[key] = VOCAB_MAPS[key].get(value, UNK_INDEX)

        all_features.append(features)

        children = element.children
        if children:
            all_features.extend(_flatten_and_extract_cats(children))

    return all_features


def extract_categorical_features(document_model: DocumentModel):
    elements = document_model.root.children
    if not elements:
        return {}

    flat_features_list = _flatten_and_extract_cats(elements)

    feature_dict = {key: [] for key in FEATURE_MAPPING.get("categorical", [])}
    for item in flat_features_list:
        for key in feature_dict.keys():
            feature_dict[key].append(item[key])

    for key in feature_dict.keys():
        feature_dict[key] = np.array(feature_dict[key], dtype=np.int32).reshape(-1, 1)

    return feature_dict
