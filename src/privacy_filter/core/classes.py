from pydantic import BaseModel, Field


class FilterRequest(BaseModel):
    items: list[str] = Field(..., min_length=1, max_length=256)
    mask: bool = True
    threshold: float = Field(0.5, ge=0.0, le=1.0)


class Span(BaseModel):
    category: str
    text: str
    start: int
    end: int
    score: float


class FilterResult(BaseModel):
    masked_text: str | None
    spans: list[Span]


class FilterResponse(BaseModel):
    results: list[FilterResult]
    model_id: str
    num_items: int
