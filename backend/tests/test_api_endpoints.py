"""API integration test verifying all Flask backend endpoints."""
import json
import sys
import unittest
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000/api"


class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import time
        for _ in range(15):
            try:
                urllib.request.urlopen(f"{BASE_URL}/health", timeout=1)
                return
            except Exception:
                time.sleep(1)

    def test_01_health(self):
        res = urllib.request.urlopen(f"{BASE_URL}/health")
        data = json.loads(res.read().decode())
        self.assertEqual(data.get("status"), "ok")

    def test_02_artifacts_list(self):
        res = urllib.request.urlopen(f"{BASE_URL}/artifacts")
        data = json.loads(res.read().decode())
        self.assertIn("artifacts", data)
        self.assertGreaterEqual(len(data["artifacts"]), 50)
        first = data["artifacts"][0]
        self.assertTrue(first["image_path"].startswith("/artifacts/"))

    def test_03_artifact_detail(self):
        res = urllib.request.urlopen(f"{BASE_URL}/artifacts/ART001")
        data = json.loads(res.read().decode())
        self.assertEqual(data["artifact"]["name"], "The Thinker")
        self.assertIn("exhibitions", data)

    def test_04_galleries(self):
        res = urllib.request.urlopen(f"{BASE_URL}/galleries")
        data = json.loads(res.read().decode())
        self.assertIn("galleries", data)
        self.assertGreater(len(data["galleries"]), 0)

    def test_05_exhibitions(self):
        res = urllib.request.urlopen(f"{BASE_URL}/exhibitions")
        data = json.loads(res.read().decode())
        self.assertIn("exhibitions", data)

    def test_06_search(self):
        req = urllib.request.Request(
            f"{BASE_URL}/search",
            data=json.dumps({"query": "Rodin bronze", "method": "bm25"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode())
        self.assertIn("results", data)
        self.assertGreater(len(data["results"]), 0)

    def test_07_chat_flow(self):
        req1 = urllib.request.Request(
            f"{BASE_URL}/chat",
            data=json.dumps({"query": "Tell me about The Thinker."}).encode(),
            headers={"Content-Type": "application/json"},
        )
        res1 = urllib.request.urlopen(req1)
        data1 = json.loads(res1.read().decode())
        session_id = data1.get("session_id")
        self.assertIsNotNone(session_id)
        self.assertEqual(data1.get("intent"), "GET_ARTIFACT_INFO")

        req2 = urllib.request.Request(
            f"{BASE_URL}/chat",
            data=json.dumps({"query": "Who created it?", "session_id": session_id}).encode(),
            headers={"Content-Type": "application/json"},
        )
        res2 = urllib.request.urlopen(req2)
        data2 = json.loads(res2.read().decode())
        self.assertEqual(data2.get("intent"), "GET_CREATOR")
        self.assertIn("Rodin", data2.get("answer", "") + str(data2.get("slots")))


if __name__ == "__main__":
    unittest.main()
