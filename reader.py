"""
reader.py — OCR engine for the License Plate Recognition System.
Uses EasyOCR to extract text from a cropped plate image.
Returns the cleaned plate string and confidence score.
"""

import easyocr
import numpy as np
from utils import preprocess_for_ocr
from config import settings
from typing import Tuple, Optional

# Load the EasyOCR reader once at module level — supports English.
_reader = easyocr.Reader(['en'])


def read_plate(plate_image: np.ndarray) -> Tuple[Optional[str], Optional[float]]:
    """
    Extract text from a cropped license plate image.

    Args:
        plate_image: Cropped BGR image of the license plate region.

    Returns:
        (plate_text, confidence) if successful,
        (None, None) if the text could not be read or confidence is too low.
    """
    if plate_image is None or plate_image.size == 0:
        return None, None

    # 1. Preprocess – enhance contrast and binarize
    clean_plate = preprocess_for_ocr(plate_image)

    # 2. Run OCR
    results = _reader.readtext(clean_plate)

    if not results:
        return None, None

    # 3. Extract the result with the highest confidence
    best_result = max(results, key=lambda r: r[2])  # r[2] is confidence
    raw_text = best_result[1]
    confidence = best_result[2]

    # 4. Clean the text: uppercase, remove non‑alphanumeric except hyphens
    cleaned = ''.join(c for c in raw_text.upper() if c.isalnum() or c == '-').strip()

    if not cleaned:
        return None, None

    # 5. Confidence filter
    if confidence < settings.detection_confidence:
        return None, None

    return cleaned, confidence