import hashlib
import logging

from app.core.config import Settings
from app.core.guardrails import enforce_input_guardrails, sanitize_output
from app.core.observability import ObservabilityTracker
from app.providers.base import LLMProvider
from app.schemas.chat import Citation
from app.services.cache_service import InMemoryTTLCache
from app.services.rag_service import LocalRAGService

logger = logging.getLogger(__name__)


class AskService:
    def __init__(
        self,
        provider: LLMProvider,
        rag_service: LocalRAGService,
        cache: InMemoryTTLCache,
        tracker: ObservabilityTracker,
        settings: Settings,
    ):
        self.provider = provider
        self.rag_service = rag_service
        self.cache = cache
        self.tracker = tracker
        self.settings = settings

    def ask(self, question: str) -> str:
        return self.provider.ask(question)

    def ask_with_context(self, question: str) -> tuple[str, list[Citation], float]:
        enforce_input_guardrails(question, self.settings)
        cache_key = self._cache_key(question)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached["answer"], cached["citations"], cached["confidence"]

        answer = sanitize_output(self.provider.ask(question))
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
        rounded_confidence = round(confidence, 4)
        result = {"answer": answer, "citations": citations, "confidence": rounded_confidence}
        self.cache.set(cache_key, result, ttl_seconds=self.settings.cache_ttl_seconds)

        token_in = max(1, len(question) // 4)
        token_out = max(1, len(answer) // 4)
        estimated_cost = (token_in + token_out) * 0.000002
        self.tracker.observe_llm_usage(token_in, token_out, estimated_cost)
        logger.info(
            "llm_usage",
            extra={"token_in": token_in, "token_out": token_out, "cost_usd": round(estimated_cost, 6)},
        )
        return answer, citations, rounded_confidence

    def readiness(self) -> tuple[bool, str | None]:
        return self.provider.readiness()

    @staticmethod
    def _cache_key(question: str) -> str:
        digest = hashlib.sha256(question.encode("utf-8")).hexdigest()
        return f"ask:{digest}"
