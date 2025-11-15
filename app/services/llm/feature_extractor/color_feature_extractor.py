import numpy as np
import re
from app.services.accessibility.analytics.json_parser.models import DocumentModel, ElementNode


def _parse_rgb(color_str):
    if not isinstance(color_str, str):
        return [0, 0, 0]

    match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str.lower())
    if match:
        return [int(c) for c in match.groups()]

    match_rgba = re.search(r'rgba\((\d+),\s*(\d+),\s*(\d+),.*?\)', color_str.lower())
    if match_rgba:
        return [int(c) for c in match_rgba.groups()]

    if color_str == 'transparent':
        return [0, 0, 0]

    return [0, 0, 0]


def _get_luminance(r, g, b):
    rgb = np.array([r, g, b]) / 255.0

    rgb = np.where(rgb <= 0.03928, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)

    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def _get_contrast_ratio(rgb1, rgb2):
    try:
        lum1 = _get_luminance(*rgb1)
        lum2 = _get_luminance(*rgb2)

        if lum1 > lum2:
            return (lum1 + 0.05) / (lum2 + 0.05)
        else:
            return (lum2 + 0.05) / (lum1 + 0.05)
    except Exception:
        return 1.0


def _flatten_and_extract_colors(elements: list[ElementNode]):
    all_color_features = []
    all_contrast_features = []

    for element in elements:
        color_str = element.color
        bg_color_str = element.backgroundColor

        rgb_color = _parse_rgb(color_str)
        rgb_bg_color = _parse_rgb(bg_color_str)

        features = (np.array(rgb_color + rgb_bg_color) / 255.0).tolist()
        all_color_features.append(features)

        contrast = _get_contrast_ratio(rgb_color, rgb_bg_color)
        all_contrast_features.append([contrast])

        children = element.children
        if children:
            child_colors, child_contrasts = _flatten_and_extract_colors(children)
            all_color_features.extend(child_colors)
            all_contrast_features.extend(child_contrasts)

    return all_color_features, all_contrast_features


def extract_color_features(document_model: DocumentModel):
    elements = document_model.root.children
    if not elements:
        return np.array([]), np.array([])

    color_matrix, contrast_matrix = _flatten_and_extract_colors(elements)

    color_matrix = np.array(color_matrix, dtype=np.float32)
    contrast_matrix = np.array(contrast_matrix, dtype=np.float32)

    return color_matrix, contrast_matrix
