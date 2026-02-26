from fastapi import APIRouter, Depends, Response

from app.api.deps import get_observability_tracker
from app.core.observability import ObservabilityTracker

router = APIRouter(tags=["observability"])


@router.get("/metrics")
async def metrics(tracker: ObservabilityTracker = Depends(get_observability_tracker)) -> Response:
    return Response(content=tracker.render_prometheus(), media_type="text/plain; version=0.0.4")
