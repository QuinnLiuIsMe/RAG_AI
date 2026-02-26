import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.incident import router as incident_router
from app.core.config import Settings, get_settings
from app.core.logging import setup_logging
from app.core.request_context import new_request_id, request_id_ctx_var
from app.providers.factory import get_provider
from app.services.ask_service import AskService
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
    app.state.rag_service = rag_service
    app.state.ask_service = AskService(get_provider(app_settings), rag_service)
    app.state.incident_service = IncidentService(rag_service)

    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or new_request_id()
        token = request_id_ctx_var.set(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            status_code = response.status_code
            return response
        except Exception:
            status_code = 500
            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                },
            )
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "request_complete",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )
            request_id_ctx_var.reset(token)

    app.include_router(chat_router)
    app.include_router(incident_router)
    app.include_router(health_router)

    @app.get("/", response_class=HTMLResponse, tags=["meta"])
    async def home() -> str:
        return "<h1>AI Ops Agent is running!</h1><p>Go to <a href='/docs'>/docs</a> to test API</p>"

    return app


app = create_app()
