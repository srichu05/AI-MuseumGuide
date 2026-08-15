"""Image preprocessing with OpenCV."""
from __future__ import annotations

import io

import cv2
import numpy as np
from PIL import Image


MAX_DIMENSION = 1024


def preprocess_image(file_bytes: bytes) -> tuple[bytes, str]:
    """Resize and normalize image for vision API. Returns (bytes, mime_type)."""
    img = Image.open(io.BytesIO(file_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > MAX_DIMENSION:
        scale = MAX_DIMENSION / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    arr = np.array(img)
    arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    arr = cv2.convertScaleAbs(arr, alpha=1.1, beta=5)

    buf = io.BytesIO()
    img_out = Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))
    img_out.save(buf, format="JPEG", quality=85)
    return buf.getvalue(), "image/jpeg"


def validate_image(file_bytes: bytes) -> tuple[bool, str]:
    if len(file_bytes) < 100:
        return False, "File too small to be a valid image"
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
        return True, ""
    except Exception as e:
        return False, f"Invalid image: {e}"
