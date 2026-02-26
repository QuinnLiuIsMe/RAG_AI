from fastapi import APIRouter, Depends

from app.api.deps import get_incident_service
from app.schemas.incident import (
    GroundedResponse,
    RecommendRemediationRequest,
    SummarizeIncidentRequest,
)
from app.services.incident_service import IncidentService

router = APIRouter(tags=["incident"])


@router.post("/summarize-incident", response_model=GroundedResponse)
async def summarize_incident(
    req: SummarizeIncidentRequest,
    service: IncidentService = Depends(get_incident_service),
) -> GroundedResponse:
    answer, citations, confidence = service.summarize_incident(req)
    return GroundedResponse(answer=answer, citations=citations, confidence=confidence)


@router.post("/recommend-remediation", response_model=GroundedResponse)
async def recommend_remediation(
    req: RecommendRemediationRequest,
    service: IncidentService = Depends(get_incident_service),
) -> GroundedResponse:
    answer, citations, confidence = service.recommend_remediation(req)
    return GroundedResponse(answer=answer, citations=citations, confidence=confidence)
