# License Plate Recognition System

A fully automated license plate recognition system that detects and reads vehicle plates from static images or a live webcam feed. When a plate is recognized, the system queries a local JSON database to identify the vehicle owner, retrieves their photo, logs a timestamp, and flags whether the vehicle is wanted. Unknown plates are automatically logged for review.

**Current version:** Detection + OCR + JSON database lookup  
**Future upgrades:** PostgreSQL support, web dashboard, multi-camera streaming

## Demo



```bash
$ python main.py --mode image --image test_images/XYZ456NG.jpg
Logged: XYZ456NG | Status: WANTED | Confidence: 0.97
Overlay shows red bounding box with "WANTED" and owner photo.

Features
Contour‑based plate detection — finds the license‑plate rectangle in complex scenes.

EasyOCR text recognition — reads plate characters with confidence scoring.

JSON database — 12 pre‑loaded entries (known, wanted, unknown) with avatar URLs.

Automatic logging — every detection is timestamped and saved as a JSON audit record.

Image & live modes — test on static photos or run continuously with webcam.

Cooldown timer — prevents spamming the same plate in live mode.

Synthetic test‑image generator — creates demo plates from the database so anyone can test instantly.

Installation
Clone the repository

bash
git clone https://github.com/InnovativeSphere/license-plate-recognition.git
cd license-plate-recognition
Create a virtual environment (recommended)
```

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # macOS/Linux
Install dependencies
```

```bash
pip install -r requirements.txt
Configure the system

Copy config.example.py → config.py

Adjust paths, camera index, confidence thresholds, and cooldown if desired.

The default values work out‑of‑the‑box for most setups.

Generate test images (optional but recommended)
```

```bash
python generate_test_plates.py
This creates test_images/*.jpg files for every plate in data/plates_db.json.

Run a test
```

```bash
python main.py --mode image --image test_images/XYZ456NG.jpg
Usage
Image mode (single photo)
bash
python main.py --mode image --image path/to/image.jpg
Detects a plate, reads it, queries the database, and displays the annotated result.

Live mode (webcam)
bash
python main.py --mode live
Continuously monitors the webcam feed. Press q to exit.
```

```
Project Structure

license_plate_recognition/
├── main.py                  # Entry point (orchestrator)
├── detector.py              # Plate localization (contour detection)
├── reader.py                # OCR engine (EasyOCR)
├── database.py              # JSON database loader & lookup
├── logger.py                # Timestamped JSON audit log
├── utils.py                 # Helpers (preprocessing, overlay, folder creation)
├── config.py                # Not committed – use config.example.py
├── config.example.py        # Template configuration
├── generate_test_plates.py  # Synthetic plate generator
├── data/
│   └── plates_db.json       # Vehicle database (12 demo entries)
├── test_images/             # Generated & sample test images
├── logs/                    # Detection logs (JSON files)
├── requirements.txt
└── README.md
Configuration Reference
All runtime settings are in config.py (Pydantic‑validated). Key values:
```
````
Setting	Default	Description
camera_index	0	Webcam to use (0 = built‑in, 1 = external)
mode	"live"	Default run mode ("image" or "live")
image_path	""	Image path when mode = "image"
detection_confidence	0.4	Minimum OCR confidence to accept a reading
cooldown_seconds	5	Seconds between consecutive detections in live mode
db_path	"data/plates_db.json"	Path to the JSON plate database
logs_folder	"logs"	Folder where audit logs are stored
known_plates_folder	"known_plates"	Folder for local owner photos (if used)
display_window	True	Show live camera feed (False for headless mode)
Database Format
data/plates_db.json contains a list of objects:


`````
JSON
{
  "plate": "ABC123NG",
  "owner": "Salim Musa",
  "photo": "https://i.pravatar.cc/150?img=1",
  "isWanted": false
}
plate – License plate string (used as lookup key).

owner – Display name.

photo – URL or local filename of the owner's image (null if unavailable).

isWanted – Boolean flag for wanted vehicles.


``````
Dependencies
opencv‑python

easyocr

pydantic

Pillow

requests

All listed in requirements.txt.

Future Upgrades
YOLOv8 plate detector – swap contour detection for a deep‑learning model.

PostgreSQL backend – replace JSON with a real database.

Web dashboard – FastAPI + live feed of recent detections.

Multi‑camera support – monitor multiple feeds simultaneously.

Face recognition integration – link driver photos to plate owners.
