"""Evaluation script for trained CNN on untouched test dataset."""
from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import sklearn.metrics as metrics
import tensorflow as tf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset" / "ai_museum_cnn"
MODEL_DIR = PROJECT_ROOT / "cnn" / "model"
MODEL_PATH = MODEL_DIR / "art_style_cnn.keras"
CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"

IMG_SIZE = (128, 128)
BATCH_SIZE = 32


def evaluate_cnn():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}")

    class_names = json.loads(CLASS_NAMES_PATH.read_text())
    print(f"Loading trained CNN model from {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH)

    test_dir = DATASET_DIR / "test"
    print(f"Loading test dataset from {test_dir}...")
    test_ds = tf.keras.utils.image_dataset_from_directory(
        test_dir,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    y_true = []
    for _, labels in test_ds:
        y_true.extend(labels.numpy())
    y_true = np.array(y_true)

    # Benchmark inference latency
    start_time = time.time()
    predictions = model.predict(test_ds)
    end_time = time.time()

    total_samples = len(y_true)
    latency_ms_per_sample = round(((end_time - start_time) / total_samples) * 1000, 2)
    y_pred = np.argmax(predictions, axis=1)

    # Compute metrics
    acc = float(metrics.accuracy_score(y_true, y_pred))
    macro_prec, macro_rec, macro_f1, _ = metrics.precision_recall_fscore_support(
        y_true, y_pred, average="macro"
    )
    weighted_prec, weighted_rec, weighted_f1, _ = metrics.precision_recall_fscore_support(
        y_true, y_pred, average="weighted"
    )
    cm = metrics.confusion_matrix(y_true, y_pred)
    cls_report = metrics.classification_report(
        y_true, y_pred, target_names=class_names, output_dict=True
    )

    # Top-3 Accuracy
    top3_correct = 0
    for i in range(total_samples):
        top3_indices = np.argsort(predictions[i])[-3:]
        if y_true[i] in top3_indices:
            top3_correct += 1
    top3_acc = float(top3_correct / total_samples)

    eval_results = {
        "model_version": "cnn-v1",
        "model_path": str(MODEL_PATH),
        "total_test_samples": total_samples,
        "test_accuracy_top1": round(acc, 4),
        "test_accuracy_top3": round(top3_acc, 4),
        "macro_precision": round(float(macro_prec), 4),
        "macro_recall": round(float(macro_rec), 4),
        "macro_f1_score": round(float(macro_f1), 4),
        "weighted_precision": round(float(weighted_prec), 4),
        "weighted_recall": round(float(weighted_rec), 4),
        "weighted_f1_score": round(float(weighted_f1), 4),
        "inference_latency_ms_per_sample": latency_ms_per_sample,
        "confusion_matrix": cm.tolist(),
        "classification_report": cls_report,
        "per_class_performance": {
            cls: {
                "precision": round(cls_report[cls]["precision"], 4),
                "recall": round(cls_report[cls]["recall"], 4),
                "f1_score": round(cls_report[cls]["f1-score"], 4),
                "support": cls_report[cls]["support"],
            }
            for cls in class_names
        },
    }

    results_path = MODEL_DIR / "evaluation_results.json"
    results_path.write_text(json.dumps(eval_results, indent=2))
    print(f"\nSaved evaluation metrics to {results_path}")

    # Plot & Save Confusion Matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
    )
    plt.title("CNN Artwork Style Classification — Confusion Matrix")
    plt.xlabel("Predicted Style")
    plt.ylabel("True Style")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    cm_path = MODEL_DIR / "confusion_matrix.png"
    plt.savefig(cm_path)
    plt.close()
    print(f"Saved confusion matrix plot to {cm_path}")

    print("\n--- CNN EVALUATION SUMMARY ---")
    print(f"Test Accuracy (Top-1): {acc * 100:.2f}%")
    print(f"Test Accuracy (Top-3): {top3_acc * 100:.2f}%")
    print(f"Macro F1-Score:        {macro_f1:.4f}")
    print(f"Weighted F1-Score:     {weighted_f1:.4f}")
    print(f"Inference Latency:     {latency_ms_per_sample} ms/sample")
    print("\nPer-Class Performance:")
    for cls in class_names:
        perf = eval_results["per_class_performance"][cls]
        print(f"  - {cls:20s}: Precision={perf['precision']:.4f}, Recall={perf['recall']:.4f}, F1={perf['f1_score']:.4f}")

    return eval_results


if __name__ == "__main__":
    evaluate_cnn()
