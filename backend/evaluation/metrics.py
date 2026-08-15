"""Evaluation metrics for NLP/IR subsystems."""
from __future__ import annotations

from typing import Any


def accuracy(y_true: list, y_pred: list) -> float:
    if not y_true:
        return 0.0
    return sum(a == b for a, b in zip(y_true, y_pred)) / len(y_true)


def precision_recall_f1(y_true: list, y_pred: list, labels: list | None = None) -> dict[str, Any]:
    labels = labels or sorted(set(y_true + y_pred))
    results = {}
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        results[label] = {"precision": prec, "recall": rec, "f1": f1}
    macro_f1 = sum(r["f1"] for r in results.values()) / len(results) if results else 0.0
    return {"per_label": results, "macro_f1": macro_f1, "accuracy": accuracy(y_true, y_pred)}


def precision_at_k(relevant: set, retrieved: list, k: int) -> float:
    top = retrieved[:k]
    if not top:
        return 0.0
    return len(set(top) & relevant) / k


def recall_at_k(relevant: set, retrieved: list, k: int) -> float:
    if not relevant:
        return 0.0
    top = retrieved[:k]
    return len(set(top) & relevant) / len(relevant)


def mrr(relevant: set, retrieved: list) -> float:
    for i, doc in enumerate(retrieved, 1):
        if doc in relevant:
            return 1.0 / i
    return 0.0


def exact_match(prediction: str, reference: str) -> float:
    return float(prediction.strip().lower() == reference.strip().lower())


def token_f1(prediction: str, reference: str) -> float:
    pred_tokens = set(prediction.lower().split())
    ref_tokens = set(reference.lower().split())
    if not pred_tokens and not ref_tokens:
        return 1.0
    if not pred_tokens or not ref_tokens:
        return 0.0
    common = pred_tokens & ref_tokens
    prec = len(common) / len(pred_tokens)
    rec = len(common) / len(ref_tokens)
    return 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0


def run_intent_evaluation():
    from nlp.intent_classifier import classify_intent, TRAINING_DATA
    y_true, y_pred = [], []
    for text, label in TRAINING_DATA:
        y_true.append(label)
        y_pred.append(classify_intent(text)["intent"])
    return precision_recall_f1(y_true, y_pred)


if __name__ == "__main__":
    print("Intent Classification Evaluation:")
    print(run_intent_evaluation())
