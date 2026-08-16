"""Local image feature/histogram matcher fallback for visual identification."""
from __future__ import annotations

import glob
from pathlib import Path
import cv2
import numpy as np
from config import DATASET_DIR

_dataset_hist_cache: dict[str, list[np.ndarray]] = {}

def _init_cache():
    global _dataset_hist_cache
    if _dataset_hist_cache:
        return
    images_dir = DATASET_DIR / "images"
    if not images_dir.exists():
        return
    for art_dir in images_dir.glob("*"):
        if art_dir.is_dir():
            art_id = art_dir.name
            hists = []
            for img_path in art_dir.glob("*.*"):
                img = cv2.imread(str(img_path))
                if img is not None:
                    h = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    cv2.normalize(h, h)
                    hists.append(h)
            if hists:
                _dataset_hist_cache[art_id] = hists

def match_local_artifact(image_bytes: bytes) -> tuple[str | None, float]:
    """Returns (artifact_id, confidence) using OpenCV histogram comparison."""
    try:
        _init_cache()
        if not _dataset_hist_cache:
            return None, 0.0

        nparr = np.frombuffer(image_bytes, np.uint8)
        query_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if query_img is None:
            return None, 0.0

        q_hist = cv2.calcHist([query_img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        cv2.normalize(q_hist, q_hist)

        best_score = -1.0
        best_art_id = None

        for art_id, hists in _dataset_hist_cache.items():
            for h in hists:
                score = cv2.compareHist(q_hist, h, cv2.HISTCMP_CORREL)
                if score > best_score:
                    best_score = score
                    best_art_id = art_id

        if best_art_id and best_score >= 0.35:
            return best_art_id, round(float(best_score), 2)
        return None, 0.0
    except Exception:
        return None, 0.0
