"""Validation script for analyzing CNN confidence, fallback frequency, confidence vs correctness, and class confusion on test set."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = PROJECT_ROOT / "cnn" / "model"
MODEL_PATH = MODEL_DIR / "art_style_cnn.keras"
CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"
TEST_DIR = PROJECT_ROOT / "dataset" / "ai_museum_cnn" / "test"

IMG_SIZE = (128, 128)
BATCH_SIZE = 32
THRESHOLD = 0.80


def run_pipeline_validation():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

    class_names = json.loads(CLASS_NAMES_PATH.read_text())
    model = tf.keras.models.load_model(MODEL_PATH)

    test_ds = tf.keras.utils.image_dataset_from_directory(
        TEST_DIR,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    y_true = []
    for _, labels in test_ds:
        y_true.extend(labels.numpy())
    y_true = np.array(y_true)

    predictions = model.predict(test_ds)
    y_pred = np.argmax(predictions, axis=1)
    confidences = np.max(predictions, axis=1)

    total_samples = len(y_true)
    accepted_count = int(np.sum(confidences >= THRESHOLD))
    fallback_count = total_samples - accepted_count
    fallback_pct = (fallback_count / total_samples) * 100.0
    avg_confidence = float(np.mean(confidences))

    # Confidence Bins
    bins = [
        ("0.00-0.49", 0.00, 0.4999),
        ("0.50-0.59", 0.50, 0.5999),
        ("0.60-0.69", 0.60, 0.6999),
        ("0.70-0.79", 0.70, 0.7999),
        ("0.80-0.89", 0.80, 0.8999),
        ("0.90-1.00", 0.90, 1.0000),
    ]

    bin_results = []
    for label, min_val, max_val in bins:
        mask = (confidences >= min_val) & (confidences <= max_val)
        bin_samples = int(np.sum(mask))
        if bin_samples > 0:
            correct_in_bin = int(np.sum((y_pred[mask] == y_true[mask])))
            bin_acc = (correct_in_bin / bin_samples) * 100.0
        else:
            correct_in_bin = 0
            bin_acc = 0.0

        bin_results.append({
            "range": label,
            "samples": bin_samples,
            "correct": correct_in_bin,
            "accuracy_pct": round(bin_acc, 2),
        })

    # Class confusion analysis
    confusion_matrix = np.zeros((len(class_names), len(class_names)), dtype=int)
    for t, p in zip(y_true, y_pred):
        confusion_matrix[t, p] += 1

    confusion_details = {}
    for i, true_cls in enumerate(class_names):
        total_cls = int(np.sum(confusion_matrix[i, :]))
        correct_cls = int(confusion_matrix[i, i])
        misclassifications = {}
        for j, pred_cls in enumerate(class_names):
            if i != j and confusion_matrix[i, j] > 0:
                misclassifications[pred_cls] = int(confusion_matrix[i, j])

        confusion_details[true_cls] = {
            "total_samples": total_cls,
            "correct": correct_cls,
            "accuracy_pct": round((correct_cls / total_cls) * 100.0, 2) if total_cls > 0 else 0.0,
            "misclassified_as": misclassifications,
        }

    report = {
        "total_test_samples": total_samples,
        "accepted_by_cnn_count": accepted_count,
        "potential_groq_fallback_count": fallback_count,
        "fallback_percentage": round(fallback_pct, 2),
        "average_cnn_confidence": round(avg_confidence, 4),
        "confidence_vs_correctness": bin_results,
        "class_confusion_details": confusion_details,
    }

    out_path = MODEL_DIR / "pipeline_validation_report.json"
    out_path.write_text(json.dumps(report, indent=2))
    print(f"\nSaved pipeline validation report to {out_path}\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    run_pipeline_validation()
