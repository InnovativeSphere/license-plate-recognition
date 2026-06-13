"""
generate_test_plates.py — Synthetic test‑image generator for the LPR system.
Reads plates_db.json and creates a clean, realistic license plate image
for every entry. Run once to populate test_images/ with demo data.

Usage:
    python generate_test_plates.py
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont


def generate_test_plates(
    db_path: str = "data/plates_db.json",
    output_folder: str = "test_images"
) -> None:
    """
    Read the plate database and generate a synthetic plate image for each entry.
    """
    # 1. Load the database
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    with open(db_path, 'r') as f:
        plates_data = json.load(f)

    # 2. Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # 3. Choose the best available bold/monospace font for clarity
    font = None
    font_paths = [
        "C:\\Windows\\Fonts\\consola.ttf",   # Windows – Consolas (monospace, very clear)
        "C:\\Windows\\Fonts\\arialbd.ttf",   # Windows – Arial Bold
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",  # Linux monospace bold
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",      # Linux sans bold
        "/System/Library/Fonts/Menlo.ttc"     # macOS – Menlo (monospace)
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, 80)  # slightly larger for clarity
            break
    if font is None:
        font = ImageFont.load_default()

    # 4. Generate one image per plate
    generated = 0
    for entry in plates_data:
        plate_number = entry.get("plate")
        if not plate_number:
            continue

        # Create blank plate: 520x120, white background
        width, height = 520, 120
        img = Image.new("RGB", (width, height), color=(255, 255, 255))

        draw = ImageDraw.Draw(img)

        # Draw a thin black border to mimic a plate frame
        border_width = 3
        draw.rectangle(
            [border_width, border_width, width - border_width - 1, height - border_width - 1],
            outline=(0, 0, 0),
            width=border_width
        )

        # Draw the plate text centered
        bbox = draw.textbbox((0, 0), plate_number, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (width - text_w) // 2
        y = (height - text_h) // 2 - 5  # slight vertical adjustment
        draw.text((x, y), plate_number, fill=(0, 0, 0), font=font)

        # Save
        out_path = os.path.join(output_folder, f"{plate_number}.jpg")
        img.save(out_path, "JPEG", quality=95)
        print(f"Generated: {out_path}")
        generated += 1

    print(f"\nDone. Generated {generated} test plate images in '{output_folder}'.")


if __name__ == "__main__":
    generate_test_plates()