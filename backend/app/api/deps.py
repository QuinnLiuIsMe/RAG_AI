from fastapi import Request

from app.core.observability import ObservabilityTracker
from app.services.ask_service import AskService
from app.services.incident_service import IncidentService


def get_ask_service(request: Request) -> AskService:
    return request.app.state.ask_service


def get_incident_service(request: Request) -> IncidentService:
    return request.app.state.incident_service


def get_observability_tracker(request: Request) -> ObservabilityTracker:
    return request.app.state.observability_tracker
