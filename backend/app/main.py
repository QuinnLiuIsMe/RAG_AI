import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.incident import router as incident_router
from app.api.routes.metrics import router as metrics_router
from app.core.auth import AuthError, decode_jwt
from app.core.config import Settings, get_settings
from app.core.guardrails import GuardrailViolation
from app.core.logging import setup_logging
from app.core.observability import ObservabilityTracker
from app.core.rate_limit import InMemoryRateLimiter
from app.core.request_context import (
    new_request_id,
    new_trace_id,
    request_id_ctx_var,
    trace_id_ctx_var,
)
from app.providers.factory import get_provider
from app.services.ask_service import AskService
from app.services.cache_service import InMemoryTTLCache
from app.services.incident_service import IncidentService
from app.services.rag_service import LocalRAGService

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    setup_logging(app_settings.log_level)

    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.app_version,
    )

    app.state.settings = app_settings
    knowledge_dir = Path(__file__).resolve().parents[1] / "data" / "knowledge_base"
    rag_service = LocalRAGService(knowledge_dir=knowledge_dir)
    rag_service.refresh_index()
    cache_service = InMemoryTTLCache()
    observability_tracker = ObservabilityTracker()

    app.state.rag_service = rag_service
    app.state.cache_service = cache_service
    app.state.observability_tracker = observability_tracker
    app.state.rate_limiter = InMemoryRateLimiter(max_requests=app_settings.rate_limit_per_minute)
    app.state.ask_service = AskService(
        get_provider(app_settings),
        rag_service,
        cache_service,
        observability_tracker,
        app_settings,
    )
    app.state.incident_service = IncidentService(
        rag_service,
        cache_service,
        observability_tracker,
        app_settings,
    )

    @app.exception_handler(GuardrailViolation)
    async def guardrail_exception_handler(_: Request, exc: GuardrailViolation):
        observability_tracker.inc("guardrail_block_total")
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or new_request_id()
        trace_id = request.headers.get("traceparent") or new_trace_id()
        token = request_id_ctx_var.set(request_id)
        trace_token = trace_id_ctx_var.set(trace_id)
        start = time.perf_counter()
        status_code = 500

        exempt_paths = {
            "/",
            "/health",
            "/ready",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/redoc",
        }
        try:
            if app_settings.auth_enabled and request.url.path not in exempt_paths:
                auth_header = request.headers.get("authorization", "")
                if not auth_header.lower().startswith("bearer "):
                    observability_tracker.inc("auth_failures_total")
                    status_code = 401
                    response = JSONResponse(status_code=status_code, content={"detail": "missing bearer token"})
                    response.headers["x-request-id"] = request_id
                    response.headers["x-trace-id"] = trace_id
                    return response
                token_value = auth_header.split(" ", 1)[1].strip()
                try:
                    principal = decode_jwt(token_value, app_settings)
                    request.state.user = principal.subject
                except AuthError as exc:
                    observability_tracker.inc("auth_failures_total")
                    status_code = 401
                    response = JSONResponse(status_code=status_code, content={"detail": str(exc)})
                    response.headers["x-request-id"] = request_id
                    response.headers["x-trace-id"] = trace_id
                    return response

            if request.url.path not in exempt_paths:
                client_host = request.client.host if request.client else "unknown"
                rate_key = f"{client_host}:{request.url.path}"
                if not app.state.rate_limiter.allow(rate_key):
                    observability_tracker.inc("rate_limit_block_total")
                    status_code = 429
                    response = JSONResponse(status_code=status_code, content={"detail": "rate limit exceeded"})
                    response.headers["x-request-id"] = request_id
                    response.headers["x-trace-id"] = trace_id
                    return response

            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            response.headers["x-trace-id"] = trace_id
            status_code = response.status_code
            return response
        except Exception:
            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                },
            )
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            observability_tracker.observe_request(status_code=status_code, duration_ms=duration_ms)
            logger.info(
                "request_complete",
                extra={
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )
            request_id_ctx_var.reset(token)
            trace_id_ctx_var.reset(trace_token)

    app.include_router(chat_router)
    app.include_router(incident_router)
    app.include_router(health_router)
    app.include_router(metrics_router)

    @app.get("/", response_class=HTMLResponse, tags=["meta"])
    async def home() -> str:
        return "<h1>AI Ops Agent is running!</h1><p>Go to <a href='/docs'>/docs</a> to test API</p>"

    return app


app = create_app()
