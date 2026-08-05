from pydantic import BaseModel


class RelevanceResult(BaseModel):
    document_index: int
    relevant: bool
    reason: str


class RelevanceResponse(BaseModel):
    results: list[RelevanceResult]