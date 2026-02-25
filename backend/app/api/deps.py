from fastapi import Request

from app.services.ask_service import AskService


def get_ask_service(request: Request) -> AskService:
    return request.app.state.ask_service
