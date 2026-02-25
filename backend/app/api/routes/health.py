from fastapi import APIRouter, Depends, Request

from app.api.deps import get_ask_service
from app.schemas.health import HealthResponse, ReadyResponse
from app.services.ask_service import AskService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(status="ok", service=settings.app_name)


@router.get("/ready", response_model=ReadyResponse)
async def ready(service: AskService = Depends(get_ask_service)) -> ReadyResponse:
    ready_state, reason = service.readiness()
    return ReadyResponse(
        status="ready" if ready_state else "not_ready",
        provider=service.provider.name,
        reason=reason,
    )
