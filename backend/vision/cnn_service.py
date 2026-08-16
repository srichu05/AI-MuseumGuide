"""Backend service wrapper for local CNN inference and confidence gating."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from config import CNN_CONFIDENCE_THRESHOLD, PROJECT_ROOT

# Ensure cnn directory is in sys.path
CNN_DIR = PROJECT_ROOT / "cnn"
if str(CNN_DIR) not in sys.path:
    sys.path.insert(0, str(CNN_DIR))

from predict import predict_style


class LocalCNNService:
    def __init__(self, threshold: float = CNN_CONFIDENCE_THRESHOLD):
        self.threshold = threshold

    def predict(self, image_bytes: bytes) -> dict[str, Any]:
        """Execute local CNN prediction and return result with confidence gating decision."""
        result = predict_style(image_bytes)
        confidence = result.get("confidence", 0.0)
        result["meets_threshold"] = bool(confidence >= self.threshold)
        result["threshold_used"] = self.threshold
        return result
