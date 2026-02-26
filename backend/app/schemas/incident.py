from pydantic import BaseModel, Field

from app.schemas.chat import Citation


class SummarizeIncidentRequest(BaseModel):
    incident: str = Field(min_length=1, max_length=6000)
    total_requests: int | None = Field(default=None, ge=0)
    error_requests: int | None = Field(default=None, ge=0)
    duration_minutes: float | None = Field(default=None, ge=0)


class RecommendRemediationRequest(BaseModel):
    incident: str = Field(min_length=1, max_length=6000)
    service_name: str | None = Field(default=None, max_length=120)


class GroundedResponse(BaseModel):
    answer: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)
