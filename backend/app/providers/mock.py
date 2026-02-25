from app.providers.base import LLMProvider


class MockLLMProvider(LLMProvider):
    name = "mock"

    def ask(self, question: str) -> str:
        return f"[mock-response] {question}"

    def readiness(self) -> tuple[bool, str | None]:
        return True, None
