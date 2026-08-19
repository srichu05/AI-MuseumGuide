"""Vision Router orchestrating local CNN style classification with GroqCloud fallback."""
from __future__ import annotations

from typing import Any

from config import CNN_CONFIDENCE_THRESHOLD
from vision.cnn_service import LocalCNNService
from vision.groq_fallback import GroqFallbackService
from vision.local_matcher import match_local_artifact


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
                - matched_artifact (dict | None)
        """
        cnn_result = self.cnn_service.predict(image_bytes)
        confidence = cnn_result.get("confidence", 0.0)

        # Check local histogram matcher as fast visual feature check
        local_matched_artifact = None
        if db_queries is not None:
            try:
                matched_art_id, match_score = match_local_artifact(image_bytes)
                if matched_art_id:
                    local_matched_artifact = db_queries.get_artifact_by_id(matched_art_id)
            except Exception:
                pass

        # High confidence -> trust local CNN
        if confidence >= self.threshold:
            return {
                "predicted_style": cnn_result.get("predicted_style", "Unknown"),
                "confidence": cnn_result.get("confidence"),
                "recognition_source": "cnn",
                "model_version": "cnn-v1",
                "raw_probabilities": cnn_result.get("raw_probabilities", {}),
                "matched_artifact": local_matched_artifact,
            }

        # Low confidence -> route to GroqCloud visual fallback
        fallback_result = self.groq_fallback_service.classify_fallback(
            image_bytes=image_bytes,
            mime_type=mime_type,
            db_queries=db_queries,
        )

        matched_art = fallback_result.get("matched_artifact") or local_matched_artifact

        return {
            "predicted_style": fallback_result.get("predicted_style", "Unknown"),
            "confidence": None,
            "recognition_source": "groq_fallback",
            "model_version": "cnn-v1",
            "matched_artifact": matched_art,
            "cnn_confidence_recorded": confidence,
            "error": fallback_result.get("error"),
        }
