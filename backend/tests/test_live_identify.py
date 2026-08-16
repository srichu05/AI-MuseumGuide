"""Integration tests for POST /api/identify endpoint using Flask test_client."""
import io
import json
import unittest
from pathlib import Path
from PIL import Image

from app import create_app

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TEST_DIR = PROJECT_ROOT / "dataset" / "ai_museum_cnn" / "test"


def create_dummy_image_bytes(color=(255, 0, 0), size=(128, 128)) -> bytes:
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestIdentifyEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_01_identify_high_confidence_image(self):
        """Test POST /api/identify with a high confidence image (confidence >= 0.80)."""
        img_path = TEST_DIR / "expressionism" / "expressionism_0145.jpg"
        if not img_path.exists():
            self.skipTest(f"Test image {img_path} not found")

        img_bytes = img_path.read_bytes()
        data = {
            "image": (io.BytesIO(img_bytes), "expressionism_0145.jpg"),
        }

        response = self.client.post("/api/identify", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 200)

        json_resp = response.get_json()
        print("\n[High Confidence Test Response]:")
        print(json.dumps(json_resp, indent=2))

        self.assertIn("predicted_style", json_resp)
        self.assertEqual(json_resp.get("recognition_source"), "cnn")
        self.assertGreaterEqual(json_resp.get("confidence", 0.0), 0.80)
        self.assertEqual(json_resp.get("model_version"), "cnn-v1")

    def test_02_identify_low_confidence_synthetic_image(self):
        """Test POST /api/identify with a synthetic image that yields low CNN confidence."""
        img_bytes = create_dummy_image_bytes(color=(128, 128, 128))
        data = {
            "image": (io.BytesIO(img_bytes), "low_conf_test.jpg"),
        }

        response = self.client.post("/api/identify", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 200)

        json_resp = response.get_json()
        print("\n[Low Confidence / Fallback Test Response]:")
        print(json.dumps(json_resp, indent=2))

        self.assertIn("predicted_style", json_resp)
        self.assertIn("recognition_source", json_resp)
        self.assertEqual(json_resp.get("model_version"), "cnn-v1")

    def test_03_identify_invalid_image(self):
        """Test POST /api/identify with corrupt non-image bytes."""
        data = {
            "image": (io.BytesIO(b"not an image file content"), "corrupt.jpg"),
        }

        response = self.client.post("/api/identify", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)

        json_resp = response.get_json()
        print("\n[Invalid Image Test Response]:")
        print(json.dumps(json_resp, indent=2))

        self.assertIn("error", json_resp)

    def test_04_identify_unsupported_extension(self):
        """Test POST /api/identify with disallowed file extension."""
        data = {
            "image": (io.BytesIO(b"dummy content"), "document.pdf"),
        }

        response = self.client.post("/api/identify", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)

        json_resp = response.get_json()
        self.assertIn("error", json_resp)


if __name__ == "__main__":
    unittest.main()
