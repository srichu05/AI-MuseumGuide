"""Unit tests for VisionRouter and confidence gating fallback edge cases."""
import unittest
from unittest.mock import MagicMock

from vision.vision_router import VisionRouter


class TestVisionRouter(unittest.TestCase):
    def test_high_confidence_routes_to_cnn(self):
        """CNN confidence >= 0.80 -> returns CNN result and GroqCloud is NOT called."""
        mock_cnn = MagicMock()
        mock_cnn.predict.return_value = {
            "predicted_style": "Impressionism",
            "confidence": 0.85,
            "recognition_source": "cnn",
            "model_version": "cnn-v1",
            "raw_probabilities": {"Impressionism": 0.85, "Realism": 0.15},
        }

        mock_fallback = MagicMock()
        router = VisionRouter(threshold=0.80, cnn_service=mock_cnn, groq_fallback_service=mock_fallback)

        res = router.route_and_identify(b"fake_image_bytes")

        self.assertEqual(res["recognition_source"], "cnn")
        self.assertEqual(res["predicted_style"], "Impressionism")
        self.assertEqual(res["confidence"], 0.85)
        self.assertEqual(res["model_version"], "cnn-v1")
        mock_fallback.classify_fallback.assert_not_called()

    def test_low_confidence_routes_to_groq_fallback(self):
        """CNN confidence < 0.80 -> triggers GroqCloud fallback, preserves CNN confidence in cnn_confidence_recorded."""
        mock_cnn = MagicMock()
        mock_cnn.predict.return_value = {
            "predicted_style": "Realism",
            "confidence": 0.55,
            "recognition_source": "cnn",
            "model_version": "cnn-v1",
        }

        mock_fallback = MagicMock()
        mock_fallback.classify_fallback.return_value = {
            "predicted_style": "Surrealism",
            "confidence": None,
            "recognition_source": "groq_fallback",
            "model_version": "cnn-v1",
            "matched_artifact": {"id": "ART005", "name": "The Persistence of Memory"},
        }

        router = VisionRouter(threshold=0.80, cnn_service=mock_cnn, groq_fallback_service=mock_fallback)

        res = router.route_and_identify(b"fake_image_bytes")

        self.assertEqual(res["recognition_source"], "groq_fallback")
        self.assertEqual(res["predicted_style"], "Surrealism")
        self.assertIsNone(res["confidence"])
        self.assertEqual(res["model_version"], "cnn-v1")
        self.assertEqual(res["cnn_confidence_recorded"], 0.55)
        self.assertEqual(res["matched_artifact"]["id"], "ART005")
        mock_fallback.classify_fallback.assert_called_once()

    def test_groq_api_failure_handled_gracefully(self):
        """GroqCloud API failure returns fallback state with error message, preventing application crash."""
        mock_cnn = MagicMock()
        mock_cnn.predict.return_value = {
            "predicted_style": "Realism",
            "confidence": 0.40,
            "recognition_source": "cnn",
            "model_version": "cnn-v1",
        }

        mock_fallback = MagicMock()
        mock_fallback.classify_fallback.return_value = {
            "predicted_style": "Unknown",
            "confidence": None,
            "recognition_source": "groq_fallback",
            "model_version": "cnn-v1",
            "matched_artifact": None,
            "error": "Groq API Connection Timeout",
        }

        router = VisionRouter(threshold=0.80, cnn_service=mock_cnn, groq_fallback_service=mock_fallback)
        res = router.route_and_identify(b"fake_image_bytes")

        self.assertEqual(res["recognition_source"], "groq_fallback")
        self.assertEqual(res["predicted_style"], "Unknown")
        self.assertIsNone(res["confidence"])
        self.assertEqual(res["error"], "Groq API Connection Timeout")

    def test_groq_invalid_json_response_handled_gracefully(self):
        """Invalid response from Groq returns Unknown style state without crashing."""
        mock_cnn = MagicMock()
        mock_cnn.predict.return_value = {
            "predicted_style": "Romanticism",
            "confidence": 0.30,
            "recognition_source": "cnn",
            "model_version": "cnn-v1",
        }

        mock_fallback = MagicMock()
        mock_fallback.classify_fallback.return_value = {
            "predicted_style": "Unknown",
            "confidence": None,
            "recognition_source": "groq_fallback",
            "model_version": "cnn-v1",
            "matched_artifact": None,
        }

        router = VisionRouter(threshold=0.80, cnn_service=mock_cnn, groq_fallback_service=mock_fallback)
        res = router.route_and_identify(b"fake_image_bytes")

        self.assertEqual(res["recognition_source"], "groq_fallback")
        self.assertEqual(res["predicted_style"], "Unknown")
        self.assertIsNone(res["confidence"])
        self.assertIsNone(res["matched_artifact"])

    def test_cnn_model_unavailable_raises_file_not_found(self):
        """Missing CNN model raises FileNotFoundError gracefully."""
        from vision.cnn_service import LocalCNNService
        cnn_service = LocalCNNService()
        cnn_service.predict = MagicMock(side_effect=FileNotFoundError("Model file missing"))

        router = VisionRouter(threshold=0.80, cnn_service=cnn_service)
        with self.assertRaises(FileNotFoundError):
            router.route_and_identify(b"fake_image_bytes")


if __name__ == "__main__":
    unittest.main()
