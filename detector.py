"""
detector.py — License plate localization engine.
Finds a rectangular plate region in a frame using contour detection.
Returns the cropped plate and its bounding box, or (None, None) if not found.
"""

import cv2
import numpy as np
from typing import Tuple, Optional


def detect_plate(frame: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[Tuple[int, int, int, int]]]:
    """
    Detect a license plate in a video frame using contour analysis.
]
    Args:
        frame: BGR image from webcam or static file.

    Returns:
        (plate_crop, (x, y, w, h)) if a plate is found,
        (None, None) otherwise.
    """
    if frame is None:
        return None, None

    # 1. Grayscale – removes colour noise, simplifies the image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2. Bilateral filter – smooths noise while preserving sharp edges
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)

    # 3. Canny edge detection – finds all strong edges
    edges = cv2.Canny(filtered, 30, 200)

    # 4. Find contours from the edge map
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 5. Sort contours by area, keep the top candidates
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    # 6. Loop through candidates and find the first rectangle
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        # 7. A license plate should have exactly 4 vertices (a rectangle)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            # Sanity check: plate should be wider than tall, and not tiny
            if w > h and w * h > 500:
                plate_crop = frame[y:y+h, x:x+w]
                return plate_crop, (x, y, w, h)

    # No plate found
    return None, None