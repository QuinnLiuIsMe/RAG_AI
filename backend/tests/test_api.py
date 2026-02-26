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
        self.assertIn("citations", response.json())
        self.assertIn("confidence", response.json())

    def test_summarize_incident_endpoint(self) -> None:
        payload = {
            "incident": "api timeout with 5xx spike and database connection saturation",
            "total_requests": 1000,
            "error_requests": 120,
            "duration_minutes": 35,
        }
        response = self.client.post("/summarize-incident", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Incident summary:", response.json()["answer"])
        self.assertIn("confidence", response.json())
        self.assertIn("citations", response.json())

    def test_recommend_remediation_endpoint(self) -> None:
        payload = {
            "incident": "db connection pool timeout and 5xx errors",
            "service_name": "orders-api",
        }
        response = self.client.post("/recommend-remediation", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Recommended remediation", response.json()["answer"])
        self.assertIn("citations", response.json())

    def test_request_id_response_header(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("x-request-id", response.headers)
        self.assertTrue(response.headers["x-request-id"])


if __name__ == "__main__":
    unittest.main()
