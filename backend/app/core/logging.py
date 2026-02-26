import json
import logging
import sys
from datetime import datetime, timezone

from app.core.request_context import get_request_id, get_trace_id


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        request_id = getattr(record, "request_id", None) or get_request_id()
        trace_id = getattr(record, "trace_id", None) or get_trace_id()
        payload: dict[str, str] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id,
            "trace_id": trace_id,
        }

        for field in ("path", "method", "status_code", "duration_ms", "token_in", "token_out", "cost_usd"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = str(value)

        return json.dumps(payload)


def setup_logging(level: str) -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)
