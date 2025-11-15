# -*- coding: utf-8 -*-

"""
Конфигурационный файл проекта.
Содержит маппинги и списки, используемые для извлечения признаков.
"""

# Словарь, определяющий, какие атрибуты элемента к какому типу признаков относятся.
# Это используется для управления процессом извлечения признаков.
FEATURE_MAPPING = {
    "textual": [
        "text",
        "alt",
        "title",
        "placeholder"
    ],
    "numeric_scalar": [
        "width",
        "height",
        "top",
        "left",
        "fontSize",
        "fontWeight",
        "lineHeight",
        "opacity",
        "letterSpacing",
        "depth",
        "num_children"
    ],
    "color": [
        "color",
        "backgroundColor"
    ],
    "categorical": [
        "tag",
        "position",
        "display",
        "textAlign"
    ]
}

# Списки известных значений для категориальных признаков.
# Это может использоваться для создания словарей (vocabularies) для Embedding-слоев
# или для One-Hot Encoding.
CATEGORICAL_VOCABULARIES = {
    "tag": [
        "div", "p", "a", "h1", "h2", "h3", "h4", "h5", "h6", 
        "button", "input", "img", "span", "li", "ul", "ol", "form", "label", "select", "option"
    ],
    "position": [
        "static", "relative", "absolute", "fixed", "sticky"
    ],
    "display": [
        "block", "inline", "inline-block", "flex", "grid", "none"
    ],
    "textAlign": [
        "left", "right", "center", "justify", "start", "end"
    ]
}
