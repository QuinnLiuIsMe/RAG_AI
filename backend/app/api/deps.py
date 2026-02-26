from fastapi import Request

from app.services.ask_service import AskService
from app.services.incident_service import IncidentService


def get_ask_service(request: Request) -> AskService:
    return request.app.state.ask_service


def get_incident_service(request: Request) -> IncidentService:
    return request.app.state.incident_service
