from fastapi import APIRouter, Depends

from app.api.deps import get_ask_service
from app.schemas.chat import QueryRequest, QueryResponse
from app.services.ask_service import AskService

router = APIRouter(tags=["chat"])


@router.post("/ask", response_model=QueryResponse)
async def ask(req: QueryRequest, service: AskService = Depends(get_ask_service)) -> QueryResponse:
    answer = service.ask(req.question)
    return QueryResponse(answer=answer)
