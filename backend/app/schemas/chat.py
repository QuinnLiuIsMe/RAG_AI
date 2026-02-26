from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class Citation(BaseModel):
    source: str
    chunk_id: str
    excerpt: str
    score: float = Field(ge=0.0, le=1.0)


class QueryResponse(BaseModel):
    answer: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)
