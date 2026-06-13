"""
config.example.py — Template configuration for the License Plate Recognition System.
Rename this file to config.py and fill in your actual values.
DO NOT commit config.py to version control — it may contain local paths or future secrets.
"""

from pydantic import BaseModel, Field, field_validator


class Settings(BaseModel):
    # ---- Camera / Input ----
    camera_index: int = Field(default=0, ge=0)
    mode: str = Field(default="live")
    image_path: str = Field(default="")   # fill when using image mode

    # ---- Detection & OCR ----
    detection_confidence: float = Field(default=0.4, gt=0.0, le=1.0)
    cooldown_seconds: int = Field(default=5, ge=0)

    # ---- File Paths ----
    db_path: str = Field(default="data/plates_db.json")
    logs_folder: str = Field(default="logs")
    known_plates_folder: str = Field(default="known_plates")

    # ---- Display ----
    display_window: bool = Field(default=True)

    # ---- Validators ----
    @field_validator('mode')
    @classmethod
    def check_mode(cls, v):
        if v not in ('image', 'live'):
            raise ValueError(f"mode must be 'image' or 'live', got '{v}'")
        return v

    @field_validator('db_path', 'logs_folder', 'known_plates_folder')
    @classmethod
    def no_trailing_slash(cls, v):
        return v.rstrip('/\\')


settings = Settings()