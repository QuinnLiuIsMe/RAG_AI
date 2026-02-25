import unittest

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        settings = Settings(app_env="test", llm_provider="mock")
        app = create_app(settings)
        self.client = TestClient(app)

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["service"], "AI Ops Agent")

    def test_ready_endpoint(self) -> None:
        response = self.client.get("/ready")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ready")
        self.assertEqual(response.json()["provider"], "mock")

    def test_ask_endpoint(self) -> None:
        response = self.client.post("/ask", json={"question": "what is cpu error trend?"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("[mock-response]", response.json()["answer"])

    def test_request_id_response_header(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("x-request-id", response.headers)
        self.assertTrue(response.headers["x-request-id"])


if __name__ == "__main__":
    unittest.main()
