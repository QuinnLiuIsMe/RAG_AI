import hashlib

from app.core.config import Settings
from app.core.guardrails import enforce_input_guardrails, sanitize_output
from app.core.observability import ObservabilityTracker
from app.schemas.chat import Citation
from app.schemas.incident import RecommendRemediationRequest, SummarizeIncidentRequest
from app.services.cache_service import InMemoryTTLCache
from app.services.rag_service import LocalRAGService
from app.tools.metrics import calculate_error_rate, classify_incident_impact


class IncidentService:
    def __init__(
        self,
        rag_service: LocalRAGService,
        cache: InMemoryTTLCache,
        tracker: ObservabilityTracker,
        settings: Settings,
    ):
        self.rag_service = rag_service
        self.cache = cache
        self.tracker = tracker
        self.settings = settings

    def summarize_incident(self, req: SummarizeIncidentRequest) -> tuple[str, list[Citation], float]:
        enforce_input_guardrails(req.incident, self.settings)
        cache_key = self._cache_key("sum", req.incident)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached["answer"], cached["citations"], cached["confidence"]

        citations, confidence = self._citations(req.incident)
        error_rate = None
        impact = "unknown"
        if req.total_requests is not None and req.error_requests is not None:
            error_rate = calculate_error_rate(req.total_requests, req.error_requests)
            impact = classify_incident_impact(error_rate, req.duration_minutes)

        details = [f"Incident summary: {req.incident.strip()}"]
        if error_rate is not None:
            details.append(f"Estimated error rate: {error_rate:.2%}")
        if req.duration_minutes is not None:
            details.append(f"Duration observed: {req.duration_minutes:.1f} minutes")
        details.append(f"Impact level: {impact}")
        details.append("Evidence is grounded in the cited runbooks/postmortems.")

        answer = sanitize_output("\n".join(details))
        result = {"answer": answer, "citations": citations, "confidence": confidence}
        self.cache.set(cache_key, result, ttl_seconds=self.settings.cache_ttl_seconds)

        self.tracker.observe_llm_usage(max(1, len(req.incident) // 4), max(1, len(answer) // 4), 0.0)
        return answer, citations, confidence

    def recommend_remediation(
        self, req: RecommendRemediationRequest
    ) -> tuple[str, list[Citation], float]:
        enforce_input_guardrails(req.incident, self.settings)
        cache_key = self._cache_key("rec", req.incident + (req.service_name or ""))
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached["answer"], cached["citations"], cached["confidence"]

        text = req.incident.lower()
        actions: list[str] = []

        if "timeout" in text or "latency" in text:
            actions.append("Scale affected service instances and validate downstream dependency latency.")
            actions.append("Apply request timeout budget and add circuit breaker fallback.")
        if "database" in text or "db" in text or "connection" in text:
            actions.append("Check DB connection pool saturation and raise pool size within safe limits.")
            actions.append("Run slow-query sampling and cache hottest read paths.")
        if "5xx" in text or "error" in text:
            actions.append("Rollback the latest risky deployment and compare error rates by version.")
            actions.append("Enable canary rollout with automatic rollback thresholds.")
        if not actions:
            actions.append("Triage using logs/metrics traces, isolate blast radius, and apply safe rollback.")
            actions.append("Document root cause and add preventive alerting.")

        prefix = f"Recommended remediation for {req.service_name}: " if req.service_name else "Recommended remediation: "
        answer = sanitize_output(prefix + " ".join(actions[:4]))
        citations, confidence = self._citations(req.incident)
        result = {"answer": answer, "citations": citations, "confidence": confidence}
        self.cache.set(cache_key, result, ttl_seconds=self.settings.cache_ttl_seconds)
        self.tracker.observe_llm_usage(max(1, len(req.incident) // 4), max(1, len(answer) // 4), 0.0)
        return answer, citations, confidence

    def _citations(self, text: str) -> tuple[list[Citation], float]:
        retrieved = self.rag_service.retrieve(text, top_k=3)
        citations = [
            Citation(
                source=item.source,
                chunk_id=item.chunk_id,
                excerpt=item.text[:220],
                score=item.score,
            )
            for item in retrieved
        ]
        confidence = round(max((item.score for item in retrieved), default=0.0), 4)
        return citations, confidence

    @staticmethod
    def _cache_key(prefix: str, payload: str) -> str:
        return f"{prefix}:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"
