import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.services.rag_service import RetrievedChunk


class IntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        settings = Settings(app_env="test", llm_provider="mock")
        self.app = create_app(settings)
        self.client = TestClient(self.app)

    def test_ask_with_mocked_llm_and_retriever(self) -> None:
        fake_chunks = [
            RetrievedChunk(
                source="backend/data/knowledge_base/runbook_lambda_timeout_coldstart.md",
                chunk_id="lambda-1",
                text="Lambda timeout remediation details.",
                score=0.92,
            )
        ]
        with patch.object(self.app.state.ask_service.provider, "ask", return_value="mocked model answer"), patch.object(
            self.app.state.rag_service, "retrieve", return_value=fake_chunks
        ):
            response = self.client.post("/ask", json={"question": "lambda timeout"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["answer"], "mocked model answer")
            self.assertEqual(len(response.json()["citations"]), 1)
            self.assertGreaterEqual(response.json()["confidence"], 0.9)

    def test_recommend_with_mocked_retriever(self) -> None:
        fake_chunks = [
            RetrievedChunk(
                source="backend/data/knowledge_base/postmortem_lambda_throttling_dlq.md",
                chunk_id="lambda-2",
                text="Throttling analysis and remediation.",
                score=0.88,
            )
        ]
        with patch.object(self.app.state.rag_service, "retrieve", return_value=fake_chunks):
            payload = {"incident": "lambda throttling and dlq growth", "service_name": "ingestor"}
            response = self.client.post("/recommend-remediation", json=payload)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Recommended remediation", response.json()["answer"])
            self.assertEqual(len(response.json()["citations"]), 1)


if __name__ == "__main__":
    unittest.main()
