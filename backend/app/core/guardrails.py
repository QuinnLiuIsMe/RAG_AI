from __future__ import annotations

import re

from app.core.config import Settings


class GuardrailViolation(Exception):
    pass


AWS_ACCESS_KEY_PATTERN = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
GENERIC_SECRET_PATTERN = re.compile(r"(secret|api[_-]?key|token)\s*[:=]\s*[A-Za-z0-9_\-]{12,}", re.IGNORECASE)


def enforce_input_guardrails(text: str, settings: Settings) -> None:
    if len(text) > settings.guardrail_max_input_chars:
        raise GuardrailViolation("input exceeds allowed length")

    lowered = text.lower()
    blocked = [item.strip().lower() for item in settings.guardrail_blocked_phrases.split(",") if item.strip()]
    for phrase in blocked:
        if phrase and phrase in lowered:
            raise GuardrailViolation(f"blocked phrase detected: {phrase}")


def sanitize_output(text: str) -> str:
    redacted = AWS_ACCESS_KEY_PATTERN.sub("[REDACTED_AWS_ACCESS_KEY]", text)
    redacted = GENERIC_SECRET_PATTERN.sub("[REDACTED_SECRET]", redacted)
    return redacted
