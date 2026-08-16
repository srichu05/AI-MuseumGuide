"""Vision Router orchestrating local CNN style classification with GroqCloud fallback."""
from __future__ import annotations

from typing import Any

from config import CNN_CONFIDENCE_THRESHOLD
from vision.cnn_service import LocalCNNService
from vision.groq_fallback import GroqFallbackService


class VisionRouter:
    def __init__(
        self,
        threshold: float = CNN_CONFIDENCE_THRESHOLD,
        cnn_service: LocalCNNService | None = None,
        groq_fallback_service: GroqFallbackService | None = None,
    ):
        self.threshold = threshold
        self.cnn_service = cnn_service or LocalCNNService(threshold=threshold)
        self.groq_fallback_service = groq_fallback_service or GroqFallbackService()

    def route_and_identify(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        db_queries: Any = None,
    ) -> dict[str, Any]:
        """Route input image through local CNN first; fallback to GroqCloud Vision if confidence < threshold.

        Returns:
            dict with:
                - predicted_style (str)
                - confidence (float or None)
                - recognition_source ("cnn" | "groq_fallback")
                - model_version ("cnn-v1")
                - raw_probabilities (dict, present if recognition_source == "cnn")
                - matched_artifact (dict | None, present if fallback matches DB artifact)
        """
        cnn_result = self.cnn_service.predict(image_bytes)
        confidence = cnn_result.get("confidence", 0.0)

        # High confidence -> trust local CNN
        if confidence >= self.threshold:
            return {
                "predicted_style": cnn_result.get("predicted_style", "Unknown"),
                "confidence": cnn_result.get("confidence"),
                "recognition_source": "cnn",
                "model_version": "cnn-v1",
                "raw_probabilities": cnn_result.get("raw_probabilities", {}),
                "matched_artifact": None,
            }

        # Low confidence -> route to GroqCloud visual fallback
        fallback_result = self.groq_fallback_service.classify_fallback(
            image_bytes=image_bytes,
            mime_type=mime_type,
            db_queries=db_queries,
        )

        return {
            "predicted_style": fallback_result.get("predicted_style", "Unknown"),
            "confidence": None,
            "recognition_source": "groq_fallback",
            "model_version": "cnn-v1",
            "matched_artifact": fallback_result.get("matched_artifact"),
            "cnn_confidence_recorded": confidence,
            "error": fallback_result.get("error"),
        }
