"""
reader.py — OCR engine for the License Plate Recognition System.
Uses EasyOCR to extract text from a cropped plate image.
Merges multiple text regions (left‑to‑right), removes hyphens,
and truncates to a maximum of 8 characters for standard plate formats.
Returns the cleaned plate string and average confidence score.
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
        (None, None) if no text found or confidence is too low.
    """
    if plate_image is None or plate_image.size == 0:
        return None, None

    # 1. Preprocess – enhance contrast and binarize
    clean_plate = preprocess_for_ocr(plate_image)

    # 2. Run OCR – get ALL detected text regions
    results = _reader.readtext(clean_plate)

    if not results:
        return None, None

    # 3. Sort results left‑to‑right by the x‑coordinate of the bounding box
    results.sort(key=lambda r: r[0][0][0])

    # 4. Extract and merge all detected text strings
    raw_parts = [r[1] for r in results]
    merged_text = ''.join(raw_parts)

    # 5. Clean the merged text: uppercase, remove non‑alphanumeric (including hyphens)
    cleaned = ''.join(c for c in merged_text.upper() if c.isalnum()).strip()

    if not cleaned:
        return None, None

    # 6. Enforce maximum 8 characters (standard plate length)
    if len(cleaned) > 8:
        cleaned = cleaned[:8]

    # 7. Average confidence across all detected regions
    avg_confidence = sum(r[2] for r in results) / len(results)

    # 8. Confidence filter
    if avg_confidence < settings.detection_confidence:
        return None, None

    return cleaned, avg_confidence