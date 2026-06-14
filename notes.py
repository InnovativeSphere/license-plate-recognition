"""
======================================================================
   LICENSE PLATE RECOGNITION SYSTEM – MASTER REFERENCE NOTES
   From Contour Detection to Full Audit Trail — The Lou & Salim Build
======================================================================

This file is the ultimate guide to Project 3 — the License Plate
Recognition System. It covers architecture, module responsibilities,
data flow, test scenarios, lessons learned, and real‑world applications.

You can treat it as your offline mentor whenever you revisit this project.

Table of Contents:
1. Project Overview
2. File Structure & Separation of Concerns
3. Module‑by‑Module Breakdown
   - config.py
   - utils.py
   - detector.py
   - reader.py
   - database.py
   - logger.py
   - main.py
   - generate_test_plates.py
4. Pipeline Flow (Image & Live Modes)
5. Test Scenarios & Results
6. Design Principles Carried Forward
7. Biomedical & Real‑World Parallels
8. Future Upgrades
9. Final Words from Lou
======================================================================
"""

# ======================================================================
# 1. PROJECT OVERVIEW
# ======================================================================
"""
Goal:
  Build a fully automated system that detects a license plate in a
  video frame (or static image), reads the plate text using OCR,
  queries a local database to identify the owner, flags wanted
  vehicles, and logs every detection for auditing.

Core Technologies:
  - OpenCV for plate detection (contour analysis)
  - EasyOCR for text recognition
  - Pydantic for typed configuration
  - JSON for lightweight database
  - Pillow & requests for overlay photo handling
  - Custom synthetic test‑image generator

Modes:
  - image mode: processes a single photo, shows the result, then exits.
  - live mode: continuous webcam feed with cooldown control.

Status: ✅ Complete, tested, and pushed to GitHub.
"""

# ======================================================================
# 2. FILE STRUCTURE & SEPARATION OF CONCERNS
# ======================================================================
"""
Every file has ONE responsibility. This makes the system modular,
testable, and future‑proof. You can swap the detector for a YOLO model
or the database for PostgreSQL without touching any other module.

license_plate_recognition/
├── config.py               # Typed settings (Pydantic)
├── config.example.py        # Template for GitHub
├── utils.py                 # Preprocessing, overlay drawing, folder creation
├── detector.py              # Plate localization via contour detection
├── reader.py                # OCR (EasyOCR) + text cleaning
├── database.py              # JSON loader and lookup
├── logger.py                # Timestamped JSON audit trail
├── main.py                  # Orchestrator (image & live modes)
├── generate_test_plates.py  # Synthetic plate image generator
├── data/
│   └── plates_db.json       # 12 demo entries (known/wanted/unknown)
├── test_images/             # Generated & sample test plates
├── logs/                    # Detection log files
├── requirements.txt
└── README.md
"""

# ======================================================================
# 3. MODULE‑BY‑MODULE BREAKDOWN
# ======================================================================

# ----- config.py -----
"""
Central control panel. All tunable values (camera index, confidence
thresholds, cooldown, file paths) live here. Uses Pydantic BaseModel
with validators. No other file contains hardcoded numbers.

Key settings:
  - camera_index: int (0 = built‑in, 1 = external)
  - detection_confidence: float (0.4) – minimum OCR score to accept a reading
  - cooldown_seconds: int (5) – prevents spamming the same plate in live mode
  - db_path: str – path to plates_db.json
  - logs_folder: str – where detection logs are stored
  - display_window: bool – show camera feed (True) or run headless (False)
"""

# ----- utils.py -----
"""
Pure helper toolbox. Contains:
  - preprocess_for_ocr(plate_image) -> binary high‑contrast image
  - draw_result_overlay(frame, bbox, result, confidence)
    Draws bounding box (green=known, red=wanted, orange=unknown),
    overlays owner info, confidence, and fetches owner photo from URL
    (or local file) to display in the corner.
  - ensure_folder_exists(folder)
  - generate_timestamp()
No detection/OCR logic – just tools.
"""

# ----- detector.py -----
"""
Plate localization engine. Uses contour analysis to find a rectangular
license‑plate region in a frame.

Pipeline:
  1. Convert to grayscale
  2. Bilateral filter (preserves edges, reduces noise)
  3. Canny edge detection
  4. Find contours, sort by area, keep top 10
  5. Approximate each contour to a polygon
  6. Select the first contour with 4 vertices (rectangle)
  7. Sanity check: width > height, area > 500
  8. Return cropped plate & bounding box (x,y,w,h)

If no plate found, returns (None, None). This module knows nothing
about OCR or databases – it just finds rectangles.
"""

# ----- reader.py -----
"""
OCR engine. Takes the cropped plate image, runs EasyOCR, and returns
the cleaned plate text and confidence score.

Steps:
  1. Preprocess plate using utils.preprocess_for_ocr()
  2. Pass to EasyOCR reader (model loaded once at module level)
  3. Select result with highest confidence
  4. Clean: uppercase, remove non‑alphanumeric (except hyphens)
  5. Confidence filter: if below config.detection_confidence, reject

Returns (None, None) if no text or low confidence.
"""

# ----- database.py -----
"""
JSON database loader and lookup. Loads plates_db.json at startup into
a dictionary keyed by plate number for O(1) lookups.

Functions:
  - load_database(db_path) -> dict
  - lookup_plate(plate, database) -> dict

If the plate is not found, returns a structured unknown record:
  { 'plate': plate, 'owner': 'UNKNOWN', 'photo': None,
    'isWanted': None, 'is_unknown': True }

This module is completely independent – no camera, no OCR.
"""

# ----- logger.py -----
"""
Audit trail. Every detection (known, wanted, or unknown) is written as
a timestamped JSON file inside the logs/ folder.

Log entry format:
  {
    "timestamp": "2026_06_13_02_06_02",
    "plate": "XYZ456NG",
    "owner": "John Doe",
    "photo": "https://i.pravatar.cc/150?img=2",
    "isWanted": true,
    "confidence": 0.9742,
    "is_unknown": false
  }

Logs are never deleted – they are the system's memory. You can later
analyze patterns (time, location, repeat offenders) from these records.
"""

# ----- main.py -----
"""
Orchestrator. Wires all modules together and supports two modes:

Image mode (--mode image --image path):
  1. Load database
  2. Read static image
  3. detect_plate() -> crop + bbox
  4. read_plate() -> text + confidence
  5. lookup_plate() -> owner result
  6. log_detection()
  7. draw_result_overlay()
  8. Display annotated image

Live mode (--mode live):
  1. Load database, open webcam
  2. In a while loop:
     - read frame
     - detect_plate()
     - if plate found and cooldown passed:
       - read_plate()
       - lookup_plate()
       - log_detection()
       - update overlay
     - show frame (with overlay if recent detection)
     - break on 'q'

Cooldown: prevents the same plate from being logged 30 times in 10
seconds while the vehicle is stationary in the frame.
"""

# ----- generate_test_plates.py -----
"""
Standalone utility – NOT part of the live system. Reads plates_db.json
and creates a synthetic license plate image for every entry. Uses Pillow
to draw centered text on a white rectangle with a black border.

Why: zero‑friction testing. Anyone cloning the repo can generate all
test images instantly and verify the full pipeline without needing
real plate photos.

Font selection: tries Consolas (monospace, clear) > Arial Bold >
DejaVu Sans Mono > system default. Works on Windows, Linux, macOS.
"""

# ======================================================================
# 4. PIPELINE FLOW (IMAGE & LIVE MODES)
# ======================================================================
"""
Image Mode:
  [Static Image] --> detector.py --> reader.py --> database.py
      --> logger.py --> utils.draw_result_overlay() --> display

Live Mode:
  [Webcam Frame] --> detector.py --> (if plate) reader.py
      --> (if text) database.py --> logger.py
      --> utils.draw_result_overlay() --> display
      --> repeat with cooldown check
"""

# ======================================================================
# 5. TEST SCENARIOS & RESULTS
# ======================================================================
"""
We validated every branch of the system with five test cases:

1. Known, not wanted (ABC123NG) → green box, KNOWN status ✅
2. Known, wanted    (XYZ456NG) → red box, WANTED, owner photo ✅
3. Unknown plate    (UNK123NG) → orange box, UNKNOWN, logged for review ✅
4. Unreadable plate (blurred)  → detection failed gracefully, no log ✅
5. No plate in frame           → "No license plate detected" ✅

The system correctly handled every outcome without crashing.
Logs were generated for all valid detections, and the audit trail
can now be used for pattern analysis.
"""

# ======================================================================
# 6. DESIGN PRINCIPLES CARRIED FORWARD
# ======================================================================
"""
From Projects 1, 2, and 3 we learned and applied:
  - One responsibility per file
  - No hardcoded values — config.py is the single source of truth
  - Type everything — Pydantic + Python type hints
  - Handle errors gracefully — never crash silently
  - Comment the "why", not the "what"
  - Separate developer utilities (generate_test_plates.py) from runtime code
  - Test every branch — not just the happy path
"""

# ======================================================================
# 7. BIOMEDICAL & REAL‑WORLD PARALLELS
# ======================================================================
"""
This project is a direct analog to medical imaging pipelines:

  License Plate Detection          Medical Imaging
  --------------------------------- ----------------
  detector.py finds plate region   -> AI finds organ/lesion boundary
  reader.py extracts text          -> AI classifies tumor type / fracture
  database.py retrieves owner      -> EHR (patient record) lookup
  logger.py creates audit trail    -> clinical decision support log
  draw_result_overlay()            -> radiologist annotation overlay

The "detect → crop → classify → log" architecture is exactly what
you'll use for:
  - X‑ray fracture detection
  - Skin lesion analysis
  - Blood cell counting
  - Retinal disease screening

You're already building biomedical AI; you're just using different
images right now. The switch is a dataset away.
"""

# ======================================================================
# 8. FUTURE UPGRADES
# ======================================================================
"""
When you're ready to level up this project:
  - YOLOv8 plate detection: replace contour analysis with a deep
    learning model for better accuracy on angled/blurry plates.
  - PostgreSQL database: swap JSON for a real database (only
    database.py changes).
  - FastAPI web dashboard: serve live logs, add/remove plates via UI.
  - Multi‑camera support: run multiple instances in threads.
  - Face recognition: link driver's face to plate owner.

All upgrades are isolated because of the modular design.
"""

# ======================================================================
# 9. FINAL WORDS FROM Mentor
# ======================================================================
"""
Salim, this project is the capstone of everything we've built together.
You took contour detection from Chapter 8 of your OpenCV notes and
turned it into a real‑time license plate reader. You integrated OCR,
database lookups, and a full audit trail — all with the same
engineering discipline that built your intruder detector and crop
disease classifier.

You now have:
  - A portfolio of three professional‑grade computer vision systems
  - A master reference for every project
  - The intuition to see the biomedical parallels in every pipeline
  - The ability to explain a CNN as a digital pathologist

This is no longer a student's GitHub. This is an engineer's portfolio.
You are employable. You are ready. And when you're ready to build that
X‑ray fracture detector, I'll be right here.

"""