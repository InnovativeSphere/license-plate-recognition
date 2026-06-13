"""
logger.py — Detection logger for the License Plate Recognition System.
Writes every detection event (known and unknown) as a timestamped JSON log entry.
Creates an audit trail for later analysis.
"""

import json
import os
from utils import generate_timestamp


def log_detection(result: dict, confidence: float, logs_folder: str) -> None:
    """
    Write a detection event to the logs folder as a JSON file named by timestamp.

    Args:
        result: Dictionary returned by database.lookup_plate(). Contains keys:
                'plate', 'owner', 'photo', 'isWanted', and possibly 'is_unknown'.
        confidence: OCR confidence score (0-1).
        logs_folder: Path to the folder where log files are stored.
    """
    # 1. Ensure the logs folder exists
    os.makedirs(logs_folder, exist_ok=True)

    # 2. Build the log entry
    log_entry = {
        'timestamp': generate_timestamp(),
        'plate': result.get('plate', 'UNKNOWN'),
        'owner': result.get('owner', 'UNKNOWN'),
        'photo': result.get('photo', None),
        'isWanted': result.get('isWanted', None),
        'confidence': round(confidence, 4),
        'is_unknown': result.get('is_unknown', False)
    }

    # 3. Write to a JSON file named by timestamp
    filename = f"{log_entry['timestamp']}.json"
    file_path = os.path.join(logs_folder, filename)

    with open(file_path, 'w') as f:
        json.dump(log_entry, f, indent=2)

    # 4. Confirm
    status = "WANTED" if log_entry['isWanted'] else (
        "UNKNOWN" if log_entry['is_unknown'] else "KNOWN"
    )
    print(f"Logged: {log_entry['plate']} | Status: {status} | Confidence: {log_entry['confidence']:.2f}")