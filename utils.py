"""
utils.py — Reusable helper functions for the License Plate Recognition System.
Handles preprocessing, overlay drawing, folder creation, and timestamps.
No detection or OCR logic here — just pure tools.
"""

import os
import cv2
import numpy as np
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO


def preprocess_for_ocr(plate_image: np.ndarray) -> np.ndarray:
    """
    Prepare a cropped plate image for OCR by enhancing contrast and
    reducing noise. Converts to grayscale, then applies adaptive thresholding.

    Args:
        plate_image: BGR or grayscale image of the license plate.

    Returns:
        Binary thresholded image, ideal for text recognition.
    """
    # Convert to grayscale if needed
    if len(plate_image.shape) == 3:
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = plate_image.copy()

    # Adaptive thresholding — handles uneven lighting better than a fixed threshold
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    return binary


def draw_result_overlay(
    frame: np.ndarray,
    bbox: tuple,
    result: dict,
    confidence: float
) -> np.ndarray:
    """
    Draw a bounding box around the license plate and overlay owner info,
    photo, and wanted status on the full frame.

    Args:
        frame: The original BGR frame from the webcam or image.
        bbox: (x, y, w, h) bounding box of the plate.
        result: Dictionary returned by database lookup. Contains keys:
                'plate', 'owner', 'photo', 'isWanted', and possibly 'is_unknown'.
        confidence: OCR confidence score (0-100 or 0-1) to display.

    Returns:
        The annotated frame (modified in-place for performance).
    """
    x, y, w, h = bbox

    # Determine color: green for known, red for unknown or wanted
    is_unknown = result.get('is_unknown', False)
    is_wanted = result.get('isWanted', False)
    if is_wanted:
        color = (0, 0, 255)      # Red for wanted
    elif is_unknown:
        color = (0, 140, 255)    # Orange-ish for unknown
    else:
        color = (0, 255, 0)      # Green for known safe

    # Draw bounding box
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    # Prepare text lines
    owner = result.get('owner', 'UNKNOWN')
    plate = result.get('plate', 'UNKNOWN')
    status = "WANTED" if is_wanted else ("UNKNOWN" if is_unknown else "KNOWN")

    lines = [
        f"Plate: {plate}",
        f"Owner: {owner}",
        f"Status: {status}",
        f"Confidence: {confidence * 100:.1f}%" if 0 < confidence <= 1 else f"Confidence: {confidence:.1f}%"
    ]

    # Draw text background and text
    y0 = y + h + 15  # start below the bounding box
    for i, line in enumerate(lines):
        text_y = y0 + (i * 20)
        cv2.putText(frame, line, (x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # ---- Photo handling ----
    photo_ref = result.get('photo', None)
    if photo_ref is not None:
        # Attempt to load photo from URL or local path
        try:
            if photo_ref.startswith(('http://', 'https://')):
                # Download avatar from URL
                resp = requests.get(photo_ref, timeout=3)
                resp.raise_for_status()
                pil_img = Image.open(BytesIO(resp.content)).convert('RGB')
            else:
                # Assume local file in known_plates folder
                pil_img = Image.open(photo_ref).convert('RGB')

            # Resize for overlay (e.g., 80x80)
            pil_img = pil_img.resize((80, 80))
            photo_array = np.array(pil_img)
            # Convert RGB to BGR for OpenCV
            photo_bgr = cv2.cvtColor(photo_array, cv2.COLOR_RGB2BGR)

            # Place photo at top-right of the bounding box area
            h_frame, w_frame = frame.shape[:2]
            px = min(x + w + 10, w_frame - 90)
            py = max(y - 10, 10)
            frame[py:py+80, px:px+80] = photo_bgr

        except Exception as e:
            # If anything fails (network, bad file), show placeholder
            cv2.putText(frame, "No photo available", (x + w + 10, y + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    else:
        # No photo field or null — show nothing or placeholder
        pass

    return frame


def ensure_folder_exists(folder: str) -> None:
    """
    Create a folder (and any parent directories) if it doesn't already exist.

    Args:
        folder: Path to the folder.
    """
    p = os.path.normpath(folder)
    if not os.path.exists(p):
        os.makedirs(p)
        print(f"Created folder: {p}")
    else:
        print(f"Folder already exists: {p}")


def generate_timestamp() -> str:
    """
    Return a formatted timestamp string for file naming.
    Format: YYYY_MM_DD_HH_MM_SS
    """
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")