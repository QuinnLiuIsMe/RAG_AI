from __future__ import annotations

from collections import defaultdict
from threading import Lock


class ObservabilityTracker:
    def __init__(self):
        self._lock = Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._latency_ms_sum = 0.0
        self._latency_ms_count = 0.0

    def inc(self, key: str, value: float = 1.0) -> None:
        with self._lock:
            self._counters[key] += value

    def observe_request(self, status_code: int, duration_ms: float) -> None:
        with self._lock:
            self._counters["http_requests_total"] += 1
            if status_code >= 400:
                self._counters["http_requests_error_total"] += 1
            self._latency_ms_sum += duration_ms
            self._latency_ms_count += 1

    def observe_llm_usage(self, tokens_in: int, tokens_out: int, estimated_cost_usd: float) -> None:
        with self._lock:
            self._counters["llm_tokens_input_total"] += tokens_in
            self._counters["llm_tokens_output_total"] += tokens_out
            self._counters["llm_estimated_cost_usd_total"] += estimated_cost_usd

    def render_prometheus(self) -> str:
        with self._lock:
            lines = [
                "# HELP http_requests_total Total HTTP requests processed",
                "# TYPE http_requests_total counter",
                f"http_requests_total {self._counters['http_requests_total']:.0f}",
                "# HELP http_requests_error_total Total HTTP requests with 4xx/5xx",
                "# TYPE http_requests_error_total counter",
                f"http_requests_error_total {self._counters['http_requests_error_total']:.0f}",
                "# HELP http_request_latency_ms_avg Average HTTP request latency in milliseconds",
                "# TYPE http_request_latency_ms_avg gauge",
                f"http_request_latency_ms_avg {self._latency_avg_ms():.4f}",
                "# HELP llm_tokens_input_total Estimated LLM input tokens",
                "# TYPE llm_tokens_input_total counter",
                f"llm_tokens_input_total {self._counters['llm_tokens_input_total']:.0f}",
                "# HELP llm_tokens_output_total Estimated LLM output tokens",
                "# TYPE llm_tokens_output_total counter",
                f"llm_tokens_output_total {self._counters['llm_tokens_output_total']:.0f}",
                "# HELP llm_estimated_cost_usd_total Estimated cumulative LLM cost in USD",
                "# TYPE llm_estimated_cost_usd_total counter",
                f"llm_estimated_cost_usd_total {self._counters['llm_estimated_cost_usd_total']:.6f}",
                "# HELP auth_failures_total Total authentication failures",
                "# TYPE auth_failures_total counter",
                f"auth_failures_total {self._counters['auth_failures_total']:.0f}",
                "# HELP rate_limit_block_total Total requests blocked by rate limiting",
                "# TYPE rate_limit_block_total counter",
                f"rate_limit_block_total {self._counters['rate_limit_block_total']:.0f}",
                "# HELP guardrail_block_total Total requests blocked by guardrails",
                "# TYPE guardrail_block_total counter",
                f"guardrail_block_total {self._counters['guardrail_block_total']:.0f}",
                "",
            ]
        return "\n".join(lines)

    def _latency_avg_ms(self) -> float:
        if self._latency_ms_count <= 0:
            return 0.0
        return self._latency_ms_sum / self._latency_ms_count
