"""
main.py — Entry point and orchestrator for the License Plate Recognition System.
Usage:
    python main.py --mode image --image test_images/ABC123NG.jpg
    python main.py --mode live
"""

import argparse
import time
import cv2

from config import settings
from utils import draw_result_overlay, ensure_folder_exists
from detector import detect_plate
from reader import read_plate
from database import load_database, lookup_plate
from logger import log_detection


def _run_image_mode():
    """Process a single static image and display the result."""
    # 1. Load database
    db = load_database(settings.db_path)

    # 2. Read image
    frame = cv2.imread(settings.image_path)
    if frame is None:
        print(f"Error: Could not read image from {settings.image_path}")
        return

    # 3. Detect plate
    plate_crop, bbox = detect_plate(frame)
    if plate_crop is None:
        print("No license plate detected in the image.")
        cv2.imshow("No Plate Found", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    # 4. Read plate text
    plate_text, confidence = read_plate(plate_crop)
    if plate_text is None:
        print("Plate detected but text could not be read with sufficient confidence.")
        cv2.imshow("Plate Unreadable", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    # 5. Lookup owner
    result = lookup_plate(plate_text, db)

    # 6. Log detection
    log_detection(result, confidence, settings.logs_folder)

    # 7. Draw overlay
    annotated = draw_result_overlay(frame, bbox, result, confidence)

    # 8. Display
    cv2.imshow("License Plate Detection - Image Mode", annotated)
    print("Press any key to close.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def _run_live_mode():
    """Continuously monitor the webcam feed for license plates."""
    # 1. Load database
    db = load_database(settings.db_path)

    # 2. Ensure logs folder exists
    ensure_folder_exists(settings.logs_folder)

    # 3. Open webcam
    cap = cv2.VideoCapture(settings.camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera {settings.camera_index}")
        return

    last_detection_time: float | None = None
    latest_result = None       # holds the last detection for overlay persistence
    latest_bbox = None
    latest_confidence = None

    print("Live mode started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Warning: Failed to read frame.")
            continue

        # 4. Detect plate
        plate_crop, bbox = detect_plate(frame)

        if plate_crop is not None:
            now = time.time()
            # Check cooldown
            if last_detection_time is None or (now - last_detection_time) >= settings.cooldown_seconds:
                # 5. Read plate text
                plate_text, confidence = read_plate(plate_crop)
                if plate_text is not None:
                    # 6. Lookup owner
                    result = lookup_plate(plate_text, db)
                    # 7. Log detection
                    log_detection(result, confidence, settings.logs_folder)
                    # 8. Update last detection time
                    last_detection_time = now
                    # 9. Store for overlay persistence
                    latest_result = result
                    latest_bbox = bbox
                    latest_confidence = confidence

        # 10. Draw overlay if we have a recent result
        if latest_result is not None and latest_bbox is not None and latest_confidence is not None:
            draw_result_overlay(frame, latest_bbox, latest_result, latest_confidence)

        # 11. Display
        if settings.display_window:
            cv2.imshow("License Plate Detection - Live Mode", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # 12. Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Live mode stopped.")


def main():
    parser = argparse.ArgumentParser(description="License Plate Recognition System")
    parser.add_argument(
        "--mode", type=str, required=True, choices=["image", "live"],
        help="Run mode: 'image' for static photo, 'live' for webcam feed."
    )
    parser.add_argument(
        "--image", type=str, default=None,
        help="Path to the image (required for image mode)."
    )
    args = parser.parse_args()

    if args.mode == "image":
        if args.image is None:
            parser.error("--image is required for image mode")
        settings.image_path = args.image
        _run_image_mode()
    elif args.mode == "live":
        _run_live_mode()


if __name__ == "__main__":
    main()