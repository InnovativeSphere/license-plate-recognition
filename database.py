"""
database.py — JSON database loader and lookup for the LPR system.
Loads plates_db.json into memory at startup and provides O(1) lookups.
"""

import json
import os
from typing import Dict, Optional


def load_database(db_path: str) -> Dict[str, dict]:
    """
    Load the plate database from a JSON file and return a dict
    keyed by plate number for instant lookup.

    Args:
        db_path: Path to the JSON database file.

    Returns:
        Dictionary of the form: {"ABC123": {...owner record...}, ...}

    Raises:
        FileNotFoundError: If the database file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")

    with open(db_path, 'r') as f:
        data = json.load(f)

    # Convert list to dictionary keyed by plate number
    database = {}
    for entry in data:
        plate = entry.get('plate')
        if plate:
            database[plate] = entry

    print(f"Database loaded: {len(database)} plates.")
    return database


def lookup_plate(plate: str, database: Dict[str, dict]) -> dict:
    """
    Look up a license plate in the database.

    Args:
        plate: Cleaned plate string from OCR (e.g., 'ABC123NG').
        database: Dict returned by load_database().

    Returns:
        The owner record if found, otherwise a standard unknown result:
        {
            'plate': plate,
            'owner': 'UNKNOWN',
            'photo': None,
            'isWanted': None,
            'is_unknown': True
        }
    """
    if plate in database:
        return database[plate]

    # Unknown plate – return a structured unknown record
    return {
        'plate': plate,
        'owner': 'UNKNOWN',
        'photo': None,
        'isWanted': None,
        'is_unknown': True
    }