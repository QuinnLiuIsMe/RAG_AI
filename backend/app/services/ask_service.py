from app.providers.base import LLMProvider


class AskService:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def ask(self, question: str) -> str:
        return self.provider.ask(question)

    def readiness(self) -> tuple[bool, str | None]:
        return self.provider.readiness()
