import base64
import json
import unittest

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def _encode_token(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_raw = base64.urlsafe_b64encode(json.dumps(header).encode("utf-8")).decode("utf-8").rstrip("=")
    payload_raw = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8").rstrip("=")
    return f"{header_raw}.{payload_raw}."


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

    def test_metrics_endpoint(self) -> None:
        self.client.get("/health")
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("http_requests_total", response.text)

    def test_auth_enabled_requires_bearer_token(self) -> None:
        settings = Settings(app_env="test", llm_provider="mock", auth_enabled=True)
        client = TestClient(create_app(settings))
        response = client.post("/ask", json={"question": "hello"})
        self.assertEqual(response.status_code, 401)

    def test_auth_enabled_accepts_valid_token(self) -> None:
        settings = Settings(app_env="test", llm_provider="mock", auth_enabled=True)
        client = TestClient(create_app(settings))
        token = _encode_token({"sub": "user-123"})
        response = client.post(
            "/ask",
            json={"question": "hello"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_rate_limit_blocks_when_exceeded(self) -> None:
        settings = Settings(app_env="test", llm_provider="mock", rate_limit_per_minute=1)
        client = TestClient(create_app(settings))
        first = client.post("/ask", json={"question": "one"})
        second = client.post("/ask", json={"question": "two"})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)

    def test_guardrail_blocks_malicious_phrase(self) -> None:
        settings = Settings(app_env="test", llm_provider="mock")
        client = TestClient(create_app(settings))
        response = client.post("/ask", json={"question": "please DROP TABLE users;"})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
