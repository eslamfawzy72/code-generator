from pydantic import BaseModel


class RelevanceResult(BaseModel):
    document_index: int
    relevant: bool
    reason: str


class RelevanceResponse(BaseModel):
    has_relevant_documents: bool = False
    results: list[RelevanceResult]