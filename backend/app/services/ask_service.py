from app.providers.base import LLMProvider
from app.schemas.chat import Citation
from app.services.rag_service import LocalRAGService


class AskService:
    def __init__(self, provider: LLMProvider, rag_service: LocalRAGService):
        self.provider = provider
        self.rag_service = rag_service

    def ask(self, question: str) -> str:
        return self.provider.ask(question)

    def ask_with_context(self, question: str) -> tuple[str, list[Citation], float]:
        answer = self.provider.ask(question)
        retrieved = self.rag_service.retrieve(question, top_k=3)
        citations = [
            Citation(
                source=item.source,
                chunk_id=item.chunk_id,
                excerpt=item.text[:220],
                score=item.score,
            )
            for item in retrieved
        ]
        confidence = max((item.score for item in retrieved), default=0.0)
        return answer, citations, round(confidence, 4)

    def readiness(self) -> tuple[bool, str | None]:
        return self.provider.readiness()
