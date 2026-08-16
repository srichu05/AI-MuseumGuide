"""Local CNN inference module for single image artwork style prediction."""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
import tensorflow as tf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "cnn" / "model"
MODEL_PATH = MODEL_DIR / "art_style_cnn.keras"
CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"

IMG_SIZE = (128, 128)
_model: tf.keras.Model | None = None
_class_names: list[str] | None = None


def load_cnn_model() -> tuple[tf.keras.Model, list[str]]:
    global _model, _class_names
    if _model is not None and _class_names is not None:
        return _model, _class_names

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained CNN model not found at {MODEL_PATH}")
    if not CLASS_NAMES_PATH.exists():
        raise FileNotFoundError(f"Class names mapping not found at {CLASS_NAMES_PATH}")

    _model = tf.keras.models.load_model(MODEL_PATH)
    _class_names = json.loads(CLASS_NAMES_PATH.read_text())
    return _model, _class_names


def preprocess_image_bytes(image_bytes: bytes) -> np.ndarray:
    """Load, convert to RGB, resize, and reshape image bytes for CNN inference."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = img.resize(IMG_SIZE, Image.Resampling.LANCZOS)
    img_array = np.array(img, dtype=np.float32)
    img_batch = np.expand_dims(img_array, axis=0)  # Shape: (1, 128, 128, 3)
    return img_batch


def predict_style(image_bytes: bytes) -> dict[str, Any]:
    """Run local CNN inference on input image bytes.

    Returns:
        dict: {
            "predicted_style": str (Canonical title-case style name),
            "confidence": float (0.0 to 1.0 rounded to 4 decimals),
            "recognition_source": "cnn",
            "model_version": "cnn-v1"
        }
    """
    model, class_names = load_cnn_model()
    img_batch = preprocess_image_bytes(image_bytes)

    probabilities = model.predict(img_batch, verbose=0)[0]
    best_idx = int(np.argmax(probabilities))
    raw_style = class_names[best_idx]
    confidence = float(probabilities[best_idx])

    # Convert to standard Display / Title Case name (e.g., 'impressionism' -> 'Impressionism', 'post-impressionism' -> 'Post-Impressionism')
    formatted_style = "-".join(part.capitalize() for part in raw_style.split("-"))

    return {
        "predicted_style": formatted_style,
        "confidence": round(confidence, 4),
        "recognition_source": "cnn",
        "model_version": "cnn-v1",
        "raw_probabilities": {
            "-".join(p.capitalize() for p in cls.split("-")): round(float(prob), 4)
            for cls, prob in zip(class_names, probabilities)
        },
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cnn/predict.py <path_to_image>")
        sys.exit(1)

    img_path = Path(sys.argv[1])
    if not img_path.exists():
        print(f"Error: File {img_path} not found.")
        sys.exit(1)

    res = predict_style(img_path.read_bytes())
    print(json.dumps(res, indent=2))
